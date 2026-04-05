import { InputHTMLAttributes, forwardRef } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, className = "", id, ...props }, ref) => {
    const inputId = id || `input-${label?.toLowerCase().replace(/\s+/g, "-")}`;

    return (
      <div className="space-y-1">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-foreground">
            {label}
            {props.required && <span className="text-destructive ml-1">*</span>}
          </label>
        )}

        <input
          ref={ref}
          id={inputId}
          className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-ring focus:border-transparent transition-colors placeholder:text-muted-foreground ${
            error
              ? "border-destructive bg-destructive/10 text-foreground"
              : "border-input bg-background text-foreground"
          } ${className}`}
          aria-invalid={!!error}
          aria-describedby={
            error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined
          }
          {...props}
        />

        {error && (
          <p id={`${inputId}-error`} className="text-destructive text-sm">
            {error}
          </p>
        )}

        {helperText && !error && (
          <p id={`${inputId}-helper`} className="text-muted-foreground text-sm">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";
