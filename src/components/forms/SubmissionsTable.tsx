import React, { useState } from 'react';
import { 
  createColumnHelper, 
  flexRender, 
  getCoreRowModel, 
  useReactTable, 
  getPaginationRowModel,
  getSortedRowModel,
  SortingState
} from '@tanstack/react-table';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ApplicationSubmission, applicationApi, FormSchema } from '@/api/applicationApi';
import { toast } from 'sonner';
import { format } from 'date-fns';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle,
  DialogTrigger,
  DialogFooter
} from "@/components/ui/dialog";
import { Eye, Check, X, ArrowUpDown } from 'lucide-react';

interface SubmissionsTableProps {
  submissions: ApplicationSubmission[];
  formSchema: FormSchema;
  onStatusChange: () => void;
}

export function SubmissionsTable({ submissions, formSchema, onStatusChange }: SubmissionsTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [selectedSubmission, setSelectedSubmission] = useState<ApplicationSubmission | null>(null);

  const handleUpdateStatus = async (id: string, status: 'approved' | 'rejected') => {
    try {
      await applicationApi.updateSubmissionStatus(id, status);
      toast.success(`Submission ${status}`);
      onStatusChange();
      setSelectedSubmission(null);
    } catch (error) {
      toast.error('Failed to update status');
    }
  };

  const columnHelper = createColumnHelper<ApplicationSubmission>();

  // Create columns based on first 3 fields of schema + status + actions
  const previewFields = formSchema.fields.slice(0, 3);
  
  const columns = [
    columnHelper.accessor('created_at', {
      header: ({ column }) => {
        return (
          <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
            Date Submitted
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: info => format(new Date(info.getValue()), 'MMM d, yyyy HH:mm')
    }),
    ...previewFields.map(field => 
      columnHelper.accessor(row => row.data_json[field.id], {
        id: field.id,
        header: field.label,
        cell: info => {
          const val = info.getValue();
          if (Array.isArray(val)) return val.join(', ');
          return val ? String(val) : '-';
        }
      })
    ),
    columnHelper.accessor('status', {
      header: 'Status',
      cell: info => {
        const status = info.getValue();
        const variant = status === 'approved' ? 'default' : (status === 'rejected' ? 'destructive' : 'secondary');
        return <Badge variant={variant as any}>{status.toUpperCase()}</Badge>;
      }
    }),
    columnHelper.display({
      id: 'actions',
      header: 'Actions',
      cell: props => (
        <Dialog open={selectedSubmission?.id === props.row.original.id} onOpenChange={(isOpen) => !isOpen && setSelectedSubmission(null)}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm" onClick={() => setSelectedSubmission(props.row.original)}>
              <Eye className="mr-2 h-4 w-4" /> View
            </Button>
          </DialogTrigger>
          {selectedSubmission?.id === props.row.original.id && (
            <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Application Details</DialogTitle>
              </DialogHeader>
              
              <div className="space-y-6 py-4">
                <div className="flex justify-between items-center bg-muted/30 p-4 rounded-lg">
                  <div>
                    <p className="text-sm text-muted-foreground">Submitted</p>
                    <p className="font-medium">{format(new Date(selectedSubmission.created_at), 'MMM d, yyyy HH:mm')}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Status</p>
                    <Badge variant={selectedSubmission.status === 'approved' ? 'default' : (selectedSubmission.status === 'rejected' ? 'destructive' : 'secondary')}>
                      {selectedSubmission.status.toUpperCase()}
                    </Badge>
                  </div>
                </div>

                <div className="space-y-4 divide-y">
                  {formSchema.fields.map(field => (
                    <div key={field.id} className="pt-4">
                      <h4 className="font-medium text-sm text-muted-foreground mb-1">{field.label}</h4>
                      <p className="whitespace-pre-wrap">
                        {Array.isArray(selectedSubmission.data_json[field.id]) 
                          ? selectedSubmission.data_json[field.id].join(', ') 
                          : selectedSubmission.data_json[field.id] || 'Not provided'}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
              
              <DialogFooter className="flex space-x-2 sm:justify-end">
                {selectedSubmission.status !== 'approved' && (
                  <Button onClick={() => handleUpdateStatus(selectedSubmission.id, 'approved')} className="bg-green-600 hover:bg-green-700">
                    <Check className="mr-2 h-4 w-4" /> Approve
                  </Button>
                )}
                {selectedSubmission.status !== 'rejected' && (
                  <Button variant="destructive" onClick={() => handleUpdateStatus(selectedSubmission.id, 'rejected')}>
                    <X className="mr-2 h-4 w-4" /> Reject
                  </Button>
                )}
              </DialogFooter>
            </DialogContent>
          )}
        </Dialog>
      )
    })
  ];

  const table = useReactTable({
    data: submissions,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: setSorting,
    state: {
      sorting,
    }
  });

  return (
    <div className="space-y-4">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map(headerGroup => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map(row => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map(cell => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  No submissions yet.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-end space-x-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => table.previousPage()}
          disabled={!table.getCanPreviousPage()}
        >
          Previous
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => table.nextPage()}
          disabled={!table.getCanNextPage()}
        >
          Next
        </Button>
      </div>
    </div>
  );
}
