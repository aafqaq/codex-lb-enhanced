import { ScrollText } from "lucide-react";
import { useTranslation } from "react-i18next";

import { Switch } from "@/components/ui/switch";
import { buildSettingsUpdateRequest } from "@/features/settings/payload";
import type { DashboardSettings, SettingsUpdateRequest } from "@/features/settings/schemas";

export type DiagnosticsSettingsProps = {
  settings: DashboardSettings;
  busy: boolean;
  onSave: (payload: SettingsUpdateRequest) => Promise<void>;
};

export function DiagnosticsSettings({ settings, busy, onSave }: DiagnosticsSettingsProps) {
  const { t } = useTranslation();
  const save = (patch: Partial<SettingsUpdateRequest>) =>
    void onSave(buildSettingsUpdateRequest(settings, patch));

  const verbose = settings.verboseLoggingEnabled;

  return (
    <section className="flex h-full flex-col rounded-xl border bg-card p-5">
      <div className="flex flex-1 flex-col space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
              <ScrollText className="h-4 w-4 text-primary" aria-hidden="true" />
            </div>
            <div>
              <h3 className="text-sm font-semibold">{t("settings.diagnostics.title")}</h3>
              <p className="text-xs text-muted-foreground">{t("settings.diagnostics.description")}</p>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between gap-3 rounded-lg border p-3">
          <div className="min-w-0">
            <p className="text-sm font-medium">{t("settings.diagnostics.verbose.label")}</p>
            <p className="text-xs text-muted-foreground">
              {t("settings.diagnostics.verbose.description")}
            </p>
          </div>
          <Switch
            aria-label={t("settings.diagnostics.verbose.ariaLabel")}
            checked={verbose}
            disabled={busy}
            onCheckedChange={(checked) =>
              save(
                checked
                  ? { verboseLoggingEnabled: true }
                  : // Turning verbose logging off also clears the payload
                    // channel, so re-enabling later cannot silently resume
                    // writing conversation content the operator had stopped.
                    { verboseLoggingEnabled: false, verboseLoggingIncludePayloads: false },
              )
            }
          />
        </div>

        <div
          className={`flex items-center justify-between gap-3 rounded-lg border p-3 transition-opacity ${
            verbose ? "" : "opacity-50"
          }`}
        >
          <div className="min-w-0">
            <p className="text-sm font-medium">{t("settings.diagnostics.payloads.label")}</p>
            <p className="text-xs text-muted-foreground">
              {t("settings.diagnostics.payloads.description")}
            </p>
          </div>
          <Switch
            aria-label={t("settings.diagnostics.payloads.ariaLabel")}
            checked={settings.verboseLoggingIncludePayloads}
            disabled={busy || !verbose}
            onCheckedChange={(checked) => save({ verboseLoggingIncludePayloads: checked })}
          />
        </div>

        {verbose ? (
          <p className="rounded-lg border border-amber-500/20 bg-amber-500/10 px-3 py-2 text-xs text-foreground">
            {t("settings.diagnostics.activeNotice")}
          </p>
        ) : null}
      </div>
    </section>
  );
}
