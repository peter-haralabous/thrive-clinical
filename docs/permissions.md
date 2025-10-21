# Permissions Quick Start

Examples and usage patterns for role-based permissions in Sandwich.

## At a high level

We use [Django Guardian](https://django-guardian.readthedocs.io/en/stable/) to manage object level permissions.
A permission in Guardian is composed of three parts:
- permission string (eg. "view_patient")
- subject (User or Group)
- object (a model instance)

By default, the Guardian API is **explicit and declarative**. Although this can be verbose at times, it makes
permissions visible and easy to understand. For this reason, we should attempt to stick to Guardian defaults
as much as possible to avoid unnecessary abstractions.

## Use

Every model has the following default permissions out of the box: `view`, `add`, `change`, `delete`. You can
add additional custom permissions in a model's `Meta` class.

```py
class Task:
    ...

    class Meta:
        permissions = (
            ("complete_task", "Can complete an task."),
        )
```

### Assigning permissions

General rules for permission assignment:
- Use the provided `assign_perm` method from Django Guardian.
- It is best to apply default permissions to an object instance at the time of its creation.
- When assigning permissions, favour applying them to Roles (groups) over individual users.
- If a default permission like "change" isn't granular enough, use a custom permission.

```py
# Assign members of this group permissions to view this patient.
assign_perm("view_patient", role.group, patient_instance)
```

#### Handling add/create permissions

The `view`, `change`, and `delete` permissions all relate to the instance of an object, however, `add` is a
little bit different since it refers to an object instance that does not exist yet.

One option is to use `add` as a django global permission as opposed to an object permission. The problem with
this approach is that it applies the permission across all instances of `Patient` regardless of which org
they belong to. So for example, if we give a user the `add_patient` permission without an object target, that
user can create patients in all organizations.

Instead, we want to move the permission check "up" a level and attach it to the organization. This involves
introducing a custom permission on `Organization` called `create_patient`. This new permission reads as "this
user has permission to add new patients to this organization".

### Managing access

#### Views

At the view-level, we can use the [decorators](https://django-guardian.readthedocs.io/en/stable/api/decorators/)
provided by Django Guardian.

```py
@permission_required_or_403("change_organization", (Organization, "id", "organization_id"))
def organization_edit(request: AuthenticatedHttpRequest, organization_id: int) -> HttpResponse:
    ...
```

The decorator restricts access to users who have the "change_organization" permission for that particular
organization. The "lookup variable" tuple is what allows us to check the if the user has permissions on a
specific object. If we omit the lookup tuple, we would be performing a global check for anyone with the
`change_organization` role. **We should almost always be using specific object checks.**

Django Guardian gives us three view decorators: `permission_required`, `permission_required_or_403`,  and
`permission_required_or_404`.

#### has_perm method

On any `User` or `Group`, you can use the `has_perm` method to check if the user has a given permission.

```py
request.user.has_perm("view_patient", patient)
```

#### Querysets

Guardian provides a powerful helper called `get_objects_for_user` which allows us to filter objects based
on a user's permissions.

```py
provider_encounters: QuerySet = get_objects_for_user(request.user, "core.view_encounter")
```

`get_objects_for_user` returns a queryset that can be further filtered based on your needs.

## Resources

- [Django Guardian Docs](https://django-guardian.readthedocs.io/en/stable/)
