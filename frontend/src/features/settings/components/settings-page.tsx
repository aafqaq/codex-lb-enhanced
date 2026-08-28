import { Suspense, lazy, useState } from "react";
import { Settings } from "lucide-react";
import { useTranslation } from "react-i18next";
import { useLocation, useNavigate } from "react-router-dom";

import { AlertMessage } from "@/components/alert-message";
import { LoadingOverlay } from "@/components/layout/loading-overlay";
import { ApiKeysSection } from "@/features/api-keys/components/api-keys-section";
import { useAccounts } from "@/features/accounts/hooks/use-accounts";
import { FirewallSection } from "@/features/firewall/components/firewall-section";
import { ModelSourcesSettings } from "@/features/model-sources/components/model-sources-settings";
import { QuotaPlannerSection } from "@/features/quota-planner/components/quota-planner-section";
import { buildSettingsUpdateRequest } from "@/features/settings/payload";
import { AppearanceSettings } from "@/features/settings/components/appearance-settings";
import { DataRetentionSettings } from "@/features/settings/components/data-retention-settings";
import { GuestAccessSettings } from "@/features/settings/components/guest-access-settings";
import { ImportSettings } from "@/features/settings/components/import-settings";
import { PasswordSettings } from "@/features/settings/components/password-settings";
import { ResetCreditSettings } from "@/features/settings/components/reset-credit-settings";
import { RoutingSettings } from "@/features/settings/components/routing-settings";
import { SessionSettings } from "@/features/settings/components/session-settings";
import { SettingsSkeleton } from "@/features/settings/components/settings-skeleton";
import { UpstreamProxySettings } from "@/features/settings/components/upstream-proxy-settings";
import { StickySessionsSection } from "@/features/sticky-sessions/components/sticky-sessions-section";
import { useAuthStore } from "@/features/auth/hooks/use-auth";
import { useSettings, useUpstreamProxyAdmin } from "@/features/settings/hooks/use-settings";
import type { SettingsUpdateRequest } from "@/features/settings/schemas";
import { getErrorMessageOrNull } from "@/utils/errors";

const TotpSettings = lazy(() =>
  import("@/features/settings/components/totp-settings").then((m) => ({ default: m.TotpSettings })),
);

type SettingsTab = "general" | "security" | "routing" | "operations";

const TAB_HASHES: Record<SettingsTab, string> = {
  general: "#general",
  security: "#security",
  routing: "#routing",
  operations: "#operations",
};

function tabForLocation(search: string, hash: string): SettingsTab {
  if (hash === "#firewall" || hash === "#operations") return "operations";
  if (hash === "#routing") return "routing";
  if (hash === "#security") return "security";
  if (new URLSearchParams(search).get("advanced") === "1") return "routing";
  return "general";
}

export function SettingsPage() {
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<SettingsTab>(() => tabForLocation(location.search, location.hash));
  const { settingsQuery, updateSettingsMutation } = useSettings();
  const { accountsQuery } = useAccounts();
  const {
    upstreamProxyQuery,
    createEndpointMutation,
    createPoolMutation,
    addPoolMemberMutation,
    testEndpointMutation,
  } = useUpstreamProxyAdmin();
  const authMode = useAuthStore((state) => state.authMode);
  const passwordManagementEnabled = useAuthStore((state) => state.passwordManagementEnabled);
  const passwordSessionActive = useAuthStore((state) => state.passwordSessionActive);
  const canWrite = useAuthStore((state) => state.canWrite);

  const settings = settingsQuery.data;
  const busy =
    updateSettingsMutation.isPending ||
    createEndpointMutation.isPending ||
    createPoolMutation.isPending ||
    addPoolMemberMutation.isPending ||
    testEndpointMutation.isPending;
  const controlsDisabled = busy || !canWrite;
  const error =
    getErrorMessageOrNull(settingsQuery.error) ||
    getErrorMessageOrNull(upstreamProxyQuery.error) ||
    getErrorMessageOrNull(updateSettingsMutation.error) ||
    getErrorMessageOrNull(createEndpointMutation.error) ||
    getErrorMessageOrNull(createPoolMutation.error) ||
    getErrorMessageOrNull(addPoolMemberMutation.error) ||
    getErrorMessageOrNull(testEndpointMutation.error);

  const handleSave = async (payload: SettingsUpdateRequest) => {
    await updateSettingsMutation.mutateAsync(payload);
  };

  return (
    <div className="animate-fade-in-up space-y-6">
      {/* Page header */}
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight">
          <Settings className="h-5 w-5 text-primary" />
          {t("settings.page.title")}
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">{t("settings.page.subtitle")}</p>
      </div>

      {!settings ? (
        <SettingsSkeleton />
      ) : (
        <>
          {error ? <AlertMessage variant="error">{error}</AlertMessage> : null}
          {!canWrite ? (
            <div className="rounded-lg border border-primary/20 bg-primary/5 px-3 py-2 text-xs font-medium text-foreground">
              {t("settings.page.readOnlyNotice")}
            </div>
          ) : null}

          {authMode === "trusted_header" ? (
            <div className="rounded-lg border border-primary/20 bg-primary/5 px-3 py-2 text-xs font-medium text-foreground">
              {t("settings.page.trustedHeaderNotice")}
            </div>
          ) : null}

          {authMode === "disabled" ? (
            <div className="rounded-lg border border-amber-500/20 bg-amber-500/10 px-3 py-2 text-xs font-medium text-foreground">
              {t("settings.page.disabledNotice")}
            </div>
          ) : null}

          <div
            className="grid grid-cols-2 gap-1 rounded-xl border bg-muted/30 p-1 sm:grid-cols-4"
            role="tablist"
            aria-label={t("settings.tabs.ariaLabel")}
          >
            {(["general", "security", "routing", "operations"] as const).map((tab) => (
              <button
                key={tab}
                type="button"
                id={`settings-tab-${tab}`}
                role="tab"
                aria-selected={activeTab === tab}
                aria-controls={`settings-panel-${tab}`}
                className={`rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                  activeTab === tab
                    ? "bg-background text-foreground shadow-sm"
                    : "text-muted-foreground hover:bg-background/70 hover:text-foreground"
                }`}
                onClick={() => {
                  setActiveTab(tab);
                  navigate(
                    { pathname: location.pathname, search: location.search, hash: TAB_HASHES[tab] },
                    { replace: true },
                  );
                }}
              >
                {t(`settings.tabs.${tab}`)}
              </button>
            ))}
          </div>

          <section
            id={`settings-panel-${activeTab}`}
            role="tabpanel"
            aria-labelledby={`settings-tab-${activeTab}`}
            className="grid min-w-0 animate-fade-in-up grid-cols-1 gap-4 lg:grid-cols-2"
          >
            {activeTab === "general" ? (
              <>
                <AppearanceSettings />
                <ImportSettings settings={settings} busy={controlsDisabled} onSave={handleSave} />
                <ResetCreditSettings settings={settings} busy={controlsDisabled} onSave={handleSave} />
              </>
            ) : null}

            {activeTab === "security" ? (
              <>
                {canWrite ? (
                  <GuestAccessSettings
                    settings={settings}
                    busy={busy}
                    onSave={handleSave}
                    onRefresh={() => settingsQuery.refetch()}
                  />
                ) : null}
                {canWrite ? <PasswordSettings disabled={busy} /> : null}
                {canWrite && passwordManagementEnabled ? (
                  <SessionSettings settings={settings} busy={busy} onSave={handleSave} />
                ) : null}
                {canWrite && passwordManagementEnabled && passwordSessionActive ? (
                  <Suspense fallback={null}>
                    <TotpSettings settings={settings} disabled={busy} onSave={handleSave} />
                  </Suspense>
                ) : null}
                <div className="lg:col-span-2">
                  <ApiKeysSection
                    apiKeyAuthEnabled={settings.apiKeyAuthEnabled}
                    hideUpstreamQuotaFromApiKeys={settings.hideUpstreamQuotaFromApiKeys}
                    disabled={controlsDisabled}
                    onApiKeyAuthEnabledChange={(enabled) =>
                      void handleSave(buildSettingsUpdateRequest(settings, { apiKeyAuthEnabled: enabled }))
                    }
                    onHideUpstreamQuotaFromApiKeysChange={(enabled) =>
                      void handleSave(buildSettingsUpdateRequest(settings, { hideUpstreamQuotaFromApiKeys: enabled }))
                    }
                  />
                </div>
              </>
            ) : null}

            {activeTab === "routing" ? (
              <>
                <div className="lg:col-span-2">
                  <RoutingSettings
                    key={[
                      settings.openaiCacheAffinityMaxAgeSeconds,
                      settings.warmupModel,
                      settings.limitWarmupModel,
                      settings.limitWarmupPrompt,
                      settings.limitWarmupExhaustedThresholdPercent,
                      settings.limitWarmupIdleThresholdPercent,
                      settings.limitWarmupCooldownSeconds,
                      settings.proxyAccountResponseCreateLimit,
                      settings.proxyAccountStreamLimit,
                      settings.proxyAccountStreamRecoveryReserve,
                      settings.proxyApiKeyFairShareCongestionThresholdPct,
                    ].join(":")}
                    settings={settings}
                    accounts={accountsQuery.data ?? []}
                    accountsLoading={accountsQuery.isLoading}
                    busy={controlsDisabled}
                    onSave={handleSave}
                  />
                </div>
                {upstreamProxyQuery.data ? (
                  <div className="lg:col-span-2">
                    <UpstreamProxySettings
                      admin={upstreamProxyQuery.data}
                      busy={controlsDisabled}
                      onSaveSettings={handleSave}
                      onCreateEndpoint={(payload) => createEndpointMutation.mutateAsync(payload)}
                      onTestEndpoint={(endpointId) => testEndpointMutation.mutateAsync(endpointId)}
                      onCreatePool={(payload) => createPoolMutation.mutateAsync(payload)}
                      onAddPoolMember={(poolId, payload) =>
                        addPoolMemberMutation.mutateAsync({ poolId, payload })
                      }
                    />
                  </div>
                ) : null}
                <div className="lg:col-span-2">
                  <ModelSourcesSettings disabled={controlsDisabled} />
                </div>
              </>
            ) : null}

            {activeTab === "operations" ? (
              <>
                <div className="lg:col-span-2">
                  <FirewallSection disabled={controlsDisabled} />
                </div>
                <div className="lg:col-span-2">
                  <QuotaPlannerSection disabled={controlsDisabled} />
                </div>
                <div className="lg:col-span-2">
                  <StickySessionsSection disabled={controlsDisabled} />
                </div>
                <div className="lg:col-span-2">
                  <DataRetentionSettings
                    key={[
                      settings.requestLogRetentionOverrideDays,
                      settings.usageHistoryRetentionOverrideDays,
                      settings.requestLogRetentionDays,
                      settings.usageHistoryRetentionDays,
                    ].join(":")}
                    settings={settings}
                    busy={controlsDisabled}
                    onSave={handleSave}
                  />
                </div>
              </>
            ) : null}
          </section>

          <LoadingOverlay visible={!!settings && busy} label={t("settings.page.savingLabel")} />
        </>
      )}
    </div>
  );
}
