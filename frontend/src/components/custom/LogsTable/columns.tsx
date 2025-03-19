"use client"

import { ColumnDef } from "@tanstack/react-table"
import { ArrowUpDown } from "lucide-react"
import {Button} from "@/components/ui/button"

// This type is used to define the shape of our data.
// You can use a Zod schema here if you want.
export type LogData = {
  timestamp: Date

  namespace_name: string
  app_name: string
  level: string
  log_type: string
  classification: string
  message: string
}

export const columns: ColumnDef<LogData>[] = [
  {
    accessorKey: "timestamp",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Time Stamp
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
  },
  {
    accessorKey: "namespace_name",
    header: "Namespace",
  },
  {
    accessorKey: "app_name",
    header: "App",
  },
  {
    accessorKey: "classification",
    header: "Classification",
  },
  {
    accessorKey: "message",
    header: "Log",
  },
]
