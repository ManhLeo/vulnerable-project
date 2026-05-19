interface PaginationControlsProps {
  page: number;
  limit: number;
  total: number;
  onPageChange: (page: number) => void;
}

export function PaginationControls({
  page,
  limit,
  total,
  onPageChange,
}: PaginationControlsProps): JSX.Element {
  const totalPages = Math.max(1, Math.ceil(total / limit));
  const hasPrev = page > 1;
  const hasNext = page < totalPages;

  const from = total === 0 ? 0 : (page - 1) * limit + 1;
  const to = Math.min(page * limit, total);

  // Build page number window: show at most 5 pages centred around current page
  const window = 2;
  const pageNumbers: number[] = [];
  const start = Math.max(1, page - window);
  const end = Math.min(totalPages, page + window);
  for (let i = start; i <= end; i++) pageNumbers.push(i);

  const btnBase =
    "inline-flex h-7 min-w-[28px] items-center justify-center rounded-[5px] border border-gray-200 bg-white px-2 text-[11px] font-medium text-text-secondary transition-colors hover:bg-gray-50 hover:text-text-primary disabled:cursor-not-allowed disabled:opacity-40";

  const btnActive =
    "inline-flex h-7 min-w-[28px] items-center justify-center rounded-[5px] border border-primary bg-primary px-2 text-[11px] font-medium text-white";

  return (
    <nav
      className="flex items-center justify-between gap-3"
      aria-label="Pagination"
    >
      {/* Record count summary */}
      <span className="font-mono text-[11px] text-text-muted">
        {total === 0 ? "No records" : `${from}–${to} of ${total}`}
      </span>

      {/* Page buttons */}
      <div className="flex items-center gap-1">
        {/* Prev */}
        <button
          type="button"
          onClick={() => onPageChange(page - 1)}
          disabled={!hasPrev}
          className={btnBase}
          aria-label="Go to previous page"
        >
          ‹
        </button>

        {/* First page shortcut */}
        {start > 1 && (
          <>
            <button
              type="button"
              onClick={() => onPageChange(1)}
              className={btnBase}
              aria-label="Go to page 1"
            >
              1
            </button>
            {start > 2 && (
              <span className="px-1 text-[11px] text-text-muted">…</span>
            )}
          </>
        )}

        {/* Page number window */}
        {pageNumbers.map((p) => (
          <button
            key={p}
            type="button"
            onClick={() => onPageChange(p)}
            aria-label={`Go to page ${p}`}
            aria-current={p === page ? "page" : undefined}
            className={p === page ? btnActive : btnBase}
          >
            {p}
          </button>
        ))}

        {/* Last page shortcut */}
        {end < totalPages && (
          <>
            {end < totalPages - 1 && (
              <span className="px-1 text-[11px] text-text-muted">…</span>
            )}
            <button
              type="button"
              onClick={() => onPageChange(totalPages)}
              className={btnBase}
              aria-label={`Go to page ${totalPages}`}
            >
              {totalPages}
            </button>
          </>
        )}

        {/* Next */}
        <button
          type="button"
          onClick={() => onPageChange(page + 1)}
          disabled={!hasNext}
          className={btnBase}
          aria-label="Go to next page"
        >
          ›
        </button>
      </div>
    </nav>
  );
}
