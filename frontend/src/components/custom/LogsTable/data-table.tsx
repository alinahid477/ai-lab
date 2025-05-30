"use client"

import * as React from "react"
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  SortingState,
  ColumnFiltersState,
  getFilteredRowModel,
  useReactTable,
} from "@tanstack/react-table"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"


import {Button} from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { X, FileDown } from "lucide-react"
import DownloadButton from "../DownloadButton"
import {DataTableFacetedFilter} from "@/components/custom/LogsTable/data-table-faceted-filter"
import { priorities, statuses } from "./data"

import { LogData } from "./columns"
import { FacetedFilterItem } from "@/components/custom/LogsTable/data-table-faceted-filter"

import {
  LayoutGrid,
  AppWindow,
  AppWindowMac,
  Dock,
  Sticker,
  Box,
  TriangleAlert,
  CircleAlert,
  CircleX,
  ShieldAlert,
} from "lucide-react"
import { useAppContext } from "@/context/AppContext"
import { fetchData } from "@/lib/utils"
import { toast } from "sonner"
import {processAction} from "@/lib/utils"
interface DataTableProps<TData extends LogData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
}

export function DataTable<TData extends LogData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  
  const uniqueAppNames  = React.useMemo(() => {
    const appNames = data.map((row) => row.app_name);
    const appsStringArr = Array.from(new Set(appNames));
    const appsJsonArr: FacetedFilterItem[] = []
    const icons = [{id: 1, icon:AppWindow, usage:0}, {id: 2, icon:AppWindowMac, usage:0}, {id: 3, icon:Dock, usage:0}, {id: 4, icon:Sticker, usage:0}, {id: 5, icon: Box, usage: 0}];
    appsStringArr.forEach((app) => {
      let randomIcon = icons[Math.floor(Math.random() * icons.length)];
      let checkCounter = 1
      while (randomIcon.usage >= checkCounter && checkCounter < 5) {
        const availableIcons = icons.filter(icon => icon.usage < checkCounter);
        if (availableIcons.length > 0) {
          randomIcon = availableIcons[Math.floor(Math.random() * availableIcons.length)];
          randomIcon.usage += 1
        }
        
        checkCounter++;
      }
      randomIcon.usage += 1
      appsJsonArr.push({ label: app, value: app, icon: randomIcon.icon });
    });
    return appsJsonArr
  }, [data]);

  const uniqueClassificationNames = React.useMemo(() => {
    const classNames = data.map((row) => row.classification);
    const classNamesArr = Array.from(new Set(classNames));
    const classNamesJsonArr: FacetedFilterItem[] = []
    classNamesArr.forEach((className) => {
      if (!className) {
        return;
      }
      if (className.toLowerCase() === "error") {
        classNamesJsonArr.push({ label: className, value: className, icon: CircleX });
      } else if (className.toLowerCase() === "warning") {
        classNamesJsonArr.push({ label: className, value: className, icon: TriangleAlert });
      } else if (className.toLowerCase().includes("security")) {
        classNamesJsonArr.push({ label: className, value: className, icon: ShieldAlert });
      } else {
        classNamesJsonArr.push({ label: className, value: className, icon: CircleAlert });
      }
    })
    return classNamesJsonArr
  }, [data]);
  const [sorting, setSorting] = React.useState<SortingState>([])
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])
  const [pagination, setPagination] = React.useState({
    pageIndex: 0,
    pageSize: 50, // Default page size
  });
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    onColumnFiltersChange: setColumnFilters,
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      sorting,
      columnFilters,
      pagination,
    },
  })
  const [isFiltered, setIsFiltered] = React.useState(false);
  
  const { myAppContext, setMyAppContext } = useAppContext();
  const [paginationMap, setPaginationMap] = React.useState<Map<number, string>>(new Map());
  const [paginationCurrentPage, setPaginationCurrentPage] = React.useState(0);
  React.useEffect(() => {
    if(myAppContext.dataTable && myAppContext.dataTable.totalrow && myAppContext.dataTable.rowcount) {
      const totalPages = Math.ceil(myAppContext.dataTable.totalrow / myAppContext.dataTable.rowcount);
      const pageMap = new Map<number, string>();
      for (let i = 0; i < totalPages; i++) {
        const startRow = i * myAppContext.dataTable.rowcount + 1;
        const endRow = Math.min((i + 1) * myAppContext.dataTable.rowcount, myAppContext.dataTable.totalrow);
        pageMap.set(i, `${startRow}-${endRow}`);
      }
      setPaginationMap(pageMap);
      setPaginationCurrentPage(myAppContext.dataTable.page);
    }
  },[myAppContext.dataTable])


  function dataTableShowPage(pageNo: string) {
    if (pageNo !== undefined && pageNo !== null) {
      const str = "csvlogs?filepath="+myAppContext.dataTable.filepath+"&page="+ pageNo +"&rowcount=" + myAppContext.dataTable.rowcount
      fetchData(myAppContext.ENVVARS.AIBACKEND_SERVER, str)
          .then((data) => {
            setMyAppContext({...myAppContext, dataTable: data});
            setPaginationCurrentPage(parseInt(pageNo, 0));
          })
          .catch((error) => {
            console.error("Error fetching data:", error);
            toast.error("Failed to fetch data. Please try again.");
          });
    }
  }
  function getCanPreviousPage() {
    if(!myAppContext.dataTable || !myAppContext.dataTable.data) {
      return false;
    }
    if(myAppContext.dataTable.page < 1) {
      return false;
    }
    return true;
  }
  function previousPage() {
    if(myAppContext.dataTable.page > 1) {
      const str = "csvlogs?filepath="+myAppContext.dataTable.filepath+"&page="+ (myAppContext.dataTable.page -1) +"&rowcount=" + myAppContext.dataTable.rowcount
      fetchData(myAppContext.ENVVARS.AIBACKEND_SERVER, str)
          .then((data) => {
            setMyAppContext({...myAppContext, dataTable: data});
          })
          .catch((error) => {
            console.error("Error fetching data:", error);
            toast.error("Failed to fetch data. Please try again.");
          });
    }
  }

  function getCanNextPage() {
    if(!myAppContext.dataTable || !myAppContext.dataTable.data) {
      return false;
    }
    if(myAppContext.dataTable.totalrow < myAppContext.dataTable.page * myAppContext.dataTable.rowcount) {
      return false;
    }
    return true;
  }
  function nextPage() {
    if(myAppContext.dataTable.totalrow > myAppContext.dataTable.page * myAppContext.dataTable.rowcount) {
      const str = "csvlogs?filepath="+myAppContext.dataTable.filepath+"&page="+ (myAppContext.dataTable.page +1) +"&rowcount=" + myAppContext.dataTable.rowcount
      fetchData(myAppContext.ENVVARS.AIBACKEND_SERVER, str)
          .then((data) => {
            setMyAppContext({...myAppContext,dataTable: data});
          })
          .catch((error) => {
            console.error("Error fetching data:", error);
            toast.error("Failed to fetch data. Please try again.");
          });
    }
  }
  return (
    <>
      
      <div className="flex items-center justify-between pb-4">
        <div className="flex flex-1 items-center space-x-2">
          <Input
            placeholder="Search log message in this display..."
            value={(table.getColumn("message")?.getFilterValue() as string) ?? ""}
            onChange={(event) =>
              table.getColumn("message")?.setFilterValue(event.target.value)
            }
            className="max-w-sm"
          />
          {table.getColumn("classification") && (
            <DataTableFacetedFilter
              column={table.getColumn("classification")}
              title="Classification"
              options={uniqueClassificationNames}
            />
          )}
        {table.getColumn("app_name") && (
          <DataTableFacetedFilter
            column={table.getColumn("app_name")}
            title="App Name"
            options={uniqueAppNames}
          />
        )}
        {isFiltered && (
          <Button
            variant="ghost"
            onClick={() => table.resetColumnFilters()}
            className="h-8 px-2 lg:px-3"
          >
            Reset
            <X />
          </Button>
        )}
          <DownloadButton
            filepath={myAppContext.dataTable.filepath}
            downloadFilename='download.csv'  // optional
          />
        </div>
      </div>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  )
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id} className="whitespace-normal break-words">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-end space-x-2 py-4">
      <div className="flex items-center space-x-2">
          <p className="text-sm font-medium">{`Showing rows ${(myAppContext.dataTable.page * myAppContext.dataTable.rowcount) === 0 ? 1 : myAppContext.dataTable.page * myAppContext.dataTable.rowcount} - ${(myAppContext.dataTable.page * myAppContext.dataTable.rowcount + myAppContext.dataTable.rowcount) > myAppContext.dataTable.totalrow ? myAppContext.dataTable.totalrow : myAppContext.dataTable.page * myAppContext.dataTable.rowcount + myAppContext.dataTable.rowcount } of ${myAppContext.dataTable.totalrow}`}</p>
          <Select
            value={paginationCurrentPage.toString()}
            onValueChange={(value) => {
              dataTableShowPage(value)
            }}>
            <SelectTrigger className="h-8 w-[70px]">
              <SelectValue placeholder={table.getState().pagination.pageSize} />
            </SelectTrigger>
            <SelectContent side="top">
              {Array.from(paginationMap.entries()).map(([key, value]) => (
                <SelectItem key={key} value={`${key}`}>
                  {value}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={() => previousPage()} 
          disabled={!getCanPreviousPage()}>
            Previous
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => nextPage()}
          disabled={!getCanNextPage()}>
            Next
        </Button>
      </div>
    </>
  )
}
