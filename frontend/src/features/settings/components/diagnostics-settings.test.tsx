import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { DiagnosticsSettings } from "@/features/settings/components/diagnostics-settings";
import { createDashboardSettings } from "@/test/mocks/factories";

describe("DiagnosticsSettings", () => {
  it("renders both controls with copy that warns about log volume and content", () => {
    render(
      <DiagnosticsSettings
        settings={createDashboardSettings()}
        busy={false}
        onSave={vi.fn().mockResolvedValue(undefined)}
      />,
    );

    expect(screen.getByText("Diagnostic logging")).toBeInTheDocument();
    expect(screen.getByText("Verbose logging")).toBeInTheDocument();
    expect(screen.getByText("Include request and response bodies")).toBeInTheDocument();
  });

  it("keeps the payload switch unusable until verbose logging is on", () => {
    const { rerender } = render(
      <DiagnosticsSettings
        settings={createDashboardSettings({ verboseLoggingEnabled: false })}
        busy={false}
        onSave={vi.fn().mockResolvedValue(undefined)}
      />,
    );

    expect(screen.getByLabelText("Include request and response bodies in logs")).toBeDisabled();

    rerender(
      <DiagnosticsSettings
        settings={createDashboardSettings({ verboseLoggingEnabled: true })}
        busy={false}
        onSave={vi.fn().mockResolvedValue(undefined)}
      />,
    );

    expect(screen.getByLabelText("Include request and response bodies in logs")).toBeEnabled();
  });

  it("shows a reminder only while verbose logging is active", () => {
    const { rerender } = render(
      <DiagnosticsSettings
        settings={createDashboardSettings({ verboseLoggingEnabled: false })}
        busy={false}
        onSave={vi.fn().mockResolvedValue(undefined)}
      />,
    );

    expect(screen.queryByText(/Remember to turn it off/)).not.toBeInTheDocument();

    rerender(
      <DiagnosticsSettings
        settings={createDashboardSettings({ verboseLoggingEnabled: true })}
        busy={false}
        onSave={vi.fn().mockResolvedValue(undefined)}
      />,
    );

    expect(screen.getByText(/Remember to turn it off/)).toBeInTheDocument();
  });

  it("turning verbose logging off also clears the payload channel", async () => {
    const user = userEvent.setup();
    const onSave = vi.fn().mockResolvedValue(undefined);
    const settings = createDashboardSettings({
      verboseLoggingEnabled: true,
      verboseLoggingIncludePayloads: true,
    });

    render(<DiagnosticsSettings settings={settings} busy={false} onSave={onSave} />);

    await user.click(screen.getByLabelText("Enable verbose logging"));

    expect(onSave).toHaveBeenCalledTimes(1);
    const payload = onSave.mock.calls[0][0];
    // Re-enabling later must not silently resume writing conversation content.
    expect(payload.verboseLoggingEnabled).toBe(false);
    expect(payload.verboseLoggingIncludePayloads).toBe(false);
  });

  it("enabling verbose logging leaves the payload choice untouched", async () => {
    const user = userEvent.setup();
    const onSave = vi.fn().mockResolvedValue(undefined);
    const settings = createDashboardSettings({
      verboseLoggingEnabled: false,
      verboseLoggingIncludePayloads: false,
    });

    render(<DiagnosticsSettings settings={settings} busy={false} onSave={onSave} />);

    await user.click(screen.getByLabelText("Enable verbose logging"));

    expect(onSave).toHaveBeenCalledTimes(1);
    expect(onSave.mock.calls[0][0].verboseLoggingEnabled).toBe(true);
    expect(onSave.mock.calls[0][0].verboseLoggingIncludePayloads).toBe(false);
  });

  it("disables both switches when busy", () => {
    render(
      <DiagnosticsSettings
        settings={createDashboardSettings({ verboseLoggingEnabled: true })}
        busy={true}
        onSave={vi.fn().mockResolvedValue(undefined)}
      />,
    );

    for (const control of screen.getAllByRole("switch")) {
      expect(control).toBeDisabled();
    }
  });
});
