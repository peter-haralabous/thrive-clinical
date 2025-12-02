import type { Model } from 'survey-core';
import { fetchJson } from '../fetchJson';

interface UploadedFile {
  id?: string;
  name: string;
  type: string;
  content?: string;
}

const deleteFile = async (url: string, csrfToken: Args['csrfToken']) => {
  const resp = await fetch(url, {
    method: 'DELETE',
    headers: {
      'X-CSRFToken': csrfToken || '',
    },
  });

  if (resp.ok) {
    return 'success';
  }
};

interface Args {
  uploadUrl: string | null;
  deleteUrl: string | null;
  fetchUrl: string | null;
  csrfToken: string | null;
}

export function setupFileUploadInput(survey: Model, args: Args) {
  const { uploadUrl, deleteUrl, fetchUrl, csrfToken } = args;

  survey.onUploadFiles.add(async (_, options) => {
    const formData = new FormData();
    options.files.forEach((file) => {
      formData.append('file-upload', file);
    });

    if (!uploadUrl) {
      return;
    }

    try {
      const response = await fetchJson(uploadUrl, {
        method: 'POST',
        body: formData,
        // Override headers to exclude 'Content-Type' so
        // the browser sets the multipart boundary
        headers: {
          'X-CSRFToken': csrfToken || '',
        },
      });
      const uploadedFiles = options.files.map((file) => {
        const resp = response.find(
          (d: { original_filename: string }) =>
            d.original_filename === file.name,
        );
        // Store ID in the content field
        return {
          file: file,
          content: resp.id,
          name: file.name,
          type: file.type,
        };
      });
      options.callback(uploadedFiles);
    } catch (error) {
      console.error('Error: ', error);
      options.callback([], ['An error occurred during file upload.']);
    }
  });

  survey.onClearFiles.add(async (_, options) => {
    if (!options.value || options.value.length === 0) {
      return options.callback('success');
    }
    const filesToDelete = options.fileName
      ? options.value.filter(
          (item: UploadedFile) => item.name === options.fileName,
        )
      : options.value;

    // Only delete files that have been uploaded (content field contains the ID)
    // Files being uploaded won't have IDs yet
    const uploadedFiles = filesToDelete.filter(
      (file: UploadedFile) => file.content && file.content !== 'undefined',
    );

    if (uploadedFiles.length === 0) {
      return options.callback('success');
    }

    const results = await Promise.all(
      uploadedFiles.map((file: UploadedFile) => {
        const url = deleteUrl + `?id=${file.content}`;
        return deleteFile(url, csrfToken);
      }),
    );
    if (results.every((res) => res === 'success')) {
      options.callback('success');
    } else {
      options.callback('error');
    }
  });

  survey.onDownloadFile.add(async (_, options) => {
    try {
      const fileId = options.fileValue.content;

      if (!fileId || fileId === 'undefined') {
        options.callback('error');
        return;
      }

      const resp = await fetch(fetchUrl + `?id=${fileId}`);
      const blob = await resp.blob();
      const file = new File([blob], options.fileValue.name, {
        type: options.fileValue.type,
      });
      const reader = new FileReader();
      reader.onload = (e) => {
        if (e?.target) {
          options.callback('success', e.target.result);
        }
      };
      reader.readAsDataURL(file);
    } catch (error) {
      console.error('Error: ', error);
      options.callback('error');
    }
  });
}
