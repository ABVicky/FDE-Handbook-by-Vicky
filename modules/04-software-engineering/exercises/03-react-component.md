# Exercise 03 — A React `CourseFilter` component

Write `CourseFilter.tsx`:

```tsx
<CourseFilter courses={["Accounting", "Data Analytics"]} value="" onChange={(course) => …} />
```

- Renders a labelled `<select>` ("Course") with **All courses** first, then the courses sorted alphabetically
- Calls `onChange("")` when "All courses" is chosen, otherwise `onChange(courseName)`
- Shows the current `value` as selected (a *controlled* component)
- Accessible: the select has a visible `<label>`

Then:
1. Use it in your dashboard's lead list (the API's `search` already matches course names; or add a `course` query parameter to `GET /leads`).
2. Write a test with Testing Library that renders it, checks the options' order, changes the selection, and asserts `onChange` was called with the right value.
