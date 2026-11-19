import React from 'react';

export interface Column<T> {
  header: string;
  accessor?: keyof T;
  render?: (row: T, index: number) => React.ReactNode;
  width?: string;
  className?: string;
}

export interface MacTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (row: T, index: number) => string;
  isLoading?: boolean;
  emptyMessage?: string;
  onRowClick?: (row: T) => void;
  className?: string;
}

export function MacTable<T>({
  columns,
  data,
  keyExtractor,
  isLoading = false,
  emptyMessage = 'NO RECORDS CATALOGED IN THIS DESK.',
  onRowClick,
  className = '',
}: MacTableProps<T>) {
  return (
    <div
      className={`border-2 border-[#252820] bg-[#FDFBF7] shadow-[4px_4px_0px_#252820] overflow-hidden ${className}`}
    >
      <div className="overflow-x-auto">
        <table className="w-full text-left font-mono text-xs border-collapse">
          <thead>
            <tr className="bg-[#EAE2CF] border-b-2 border-[#252820] select-none text-[10px] tracking-wider uppercase text-[#252820]">
              {columns.map((col, idx) => (
                <th
                  key={idx}
                  className={`p-2.5 font-bold border-r border-[#252820]/30 last:border-r-0 ${
                    col.width || ''
                  } ${col.className || ''}`}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[#252820]/20">
            {isLoading ? (
              <tr>
                <td colSpan={columns.length} className="p-8 text-center text-[#777568] animate-pulse">
                  [RETRIEVING DATA FROM REPOSITORY...]
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="p-8 text-center text-[#777568]">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              data.map((row, rowIdx) => (
                <tr
                  key={keyExtractor(row, rowIdx)}
                  onClick={() => onRowClick?.(row)}
                  className={`hover:bg-[#EAE2CF]/60 transition-none ${
                    onRowClick ? 'cursor-pointer' : ''
                  } ${rowIdx % 2 === 1 ? 'bg-[#F9F6ED]' : 'bg-[#FDFBF7]'}`}
                >
                  {columns.map((col, colIdx) => (
                    <td
                      key={colIdx}
                      className={`p-2.5 border-r border-[#252820]/20 last:border-r-0 text-[#252820] ${
                        col.className || ''
                      }`}
                    >
                      {col.render
                        ? col.render(row, rowIdx)
                        : col.accessor
                        ? String(row[col.accessor] ?? '')
                        : null}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
