// Run inside a Vite + Vitest project (e.g. projects/admitflow/web): copy both files into src/.
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { CourseFilter } from "./CourseFilter";

// Without Vitest "globals", Testing Library can't clean up automatically: remove rendered output after each test.
afterEach(cleanup);

describe("CourseFilter", () => {
  it("lists All courses first, then courses alphabetically", () => {
    render(<CourseFilter courses={["Web Development", "Accounting"]} value="" onChange={() => {}} />);
    const options = screen.getAllByRole("option").map((o) => o.textContent);
    expect(options).toEqual(["All courses", "Accounting", "Web Development"]);
  });

  it("is labelled and reports the chosen course", () => {
    const onChange = vi.fn();
    render(<CourseFilter courses={["Accounting"]} value="" onChange={onChange} />);
    fireEvent.change(screen.getByLabelText("Course"), { target: { value: "Accounting" } });
    expect(onChange).toHaveBeenCalledWith("Accounting");
  });

  it("shows the current value as selected", () => {
    render(<CourseFilter courses={["Accounting", "Data Analytics"]} value="Data Analytics" onChange={() => {}} />);
    expect((screen.getByLabelText("Course") as HTMLSelectElement).value).toBe("Data Analytics");
  });
});
