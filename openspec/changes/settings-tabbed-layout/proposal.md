# Settings tabbed layout

## Why

The settings page currently renders every section in one long vertical stream,
which makes related controls difficult to discover and forces excessive scrolling.

## Scope

- Organize settings into four tabs: General, Access & security, Routing & accounts,
  and Operations.
- Render the selected tab as a responsive two-column card grid on wide screens and
  a single column on narrow screens.
- Mount only the selected category so hidden sections do not create unnecessary
  queries or visual noise.
- Preserve existing controls, permissions, save behavior, deep links, and mobile
  usability.

## Compatibility

No backend API, setting, persistence format, or proxy behavior changes.
