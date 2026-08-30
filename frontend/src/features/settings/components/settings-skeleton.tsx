import { Skeleton } from "@/components/ui/skeleton";

export type SettingsSkeletonTab = "general" | "security" | "routing" | "operations";

type CardShape = {
  /** Placeholder rows inside the card body. */
  rows: number;
  /** Full page width, matching a card the real tab renders as lg:col-span-2. */
  wide?: boolean;
};

/** One grid child: a single card, or a column of cards sharing one cell. */
type SlotShape = CardShape | { stack: CardShape[] };

// Mirrors what each tab actually renders, so the switch from skeleton to loaded
// content does not move the tab bar or reflow the grid. Keep in sync with the
// tab bodies in settings-page.tsx.
const TAB_SHAPES: Record<SettingsSkeletonTab, SlotShape[]> = {
  general: [{ rows: 4 }, { stack: [{ rows: 1 }, { rows: 2 }] }],
  security: [{ rows: 2 }, { rows: 1 }, { rows: 1 }, { rows: 2 }, { rows: 3, wide: true }],
  routing: [
    { rows: 5, wide: true },
    { rows: 3, wide: true },
    { rows: 2, wide: true },
  ],
  operations: [
    { rows: 3, wide: true },
    { rows: 3, wide: true },
    { rows: 2, wide: true },
    { rows: 2 },
    { rows: 2 },
  ],
};

function SkeletonCard({ rows, wide }: CardShape) {
  return (
    <div className={`min-w-0 ${wide ? "lg:col-span-2" : ""}`}>
      <div className="h-full rounded-xl border bg-card p-5">
        <div className="space-y-3">
          <div className="flex items-center gap-2.5">
            <Skeleton className="h-8 w-8 shrink-0 rounded-lg" />
            <div className="min-w-0 flex-1 space-y-1">
              <Skeleton className="h-4 w-28" />
              <Skeleton className="h-3 w-52 max-w-full" />
            </div>
          </div>
          {Array.from({ length: rows }).map((_, index) => (
            <div key={index} className="flex items-center justify-between gap-3 rounded-lg border p-3">
              <div className="min-w-0 flex-1 space-y-1">
                <Skeleton className="h-3.5 w-32 max-w-full" />
                <Skeleton className="h-3 w-56 max-w-full" />
              </div>
              <Skeleton className="h-5 w-9 shrink-0 rounded-full" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function SettingsSkeleton({ tab = "general" }: { tab?: SettingsSkeletonTab }) {
  return (
    <>
      {/* Same box as the live tab bar so it does not jump into place on load. */}
      <div className="grid grid-cols-2 gap-1 rounded-xl border bg-muted/30 p-1 sm:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="flex items-center justify-center rounded-lg px-3 py-2.5">
            {/* h-5 matches the real tab button's text-sm line box, so the bar
                keeps the same height in both states. */}
            <Skeleton className="h-5 w-16" />
          </div>
        ))}
      </div>

      <div className="grid min-w-0 auto-rows-max content-start items-stretch grid-cols-1 gap-4 lg:grid-cols-2">
        {TAB_SHAPES[tab].map((slot, index) =>
          "stack" in slot ? (
            <div key={index} className="flex min-w-0 flex-col gap-4">
              {slot.stack.map((shape, stackIndex) => (
                <SkeletonCard key={stackIndex} {...shape} />
              ))}
            </div>
          ) : (
            <SkeletonCard key={index} {...slot} />
          ),
        )}
      </div>
    </>
  );
}
