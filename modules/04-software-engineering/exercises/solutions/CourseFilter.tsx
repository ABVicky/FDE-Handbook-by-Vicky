// Exercise 03 — reference solution.
import { useId } from "react";

interface Props {
  courses: string[];
  value: string;                       // "" means all courses
  onChange: (course: string) => void;
}

export function CourseFilter({ courses, value, onChange }: Props) {
  const id = useId();                  // unique id linking <label> and <select>
  const sorted = [...courses].sort((a, b) => a.localeCompare(b));
  return (
    <span>
      <label htmlFor={id}>Course</label>{" "}
      <select id={id} value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="">All courses</option>
        {sorted.map((course) => (
          <option key={course} value={course}>{course}</option>
        ))}
      </select>
    </span>
  );
}
