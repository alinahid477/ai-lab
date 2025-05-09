import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet" 
import { useState } from "react"
import {toast} from "sonner"
import {useForm} from "react-hook-form"
import {zodResolver} from "@hookform/resolvers/zod"
import * as z from "zod"
// import {cn} from "@/lib/utils"
import {Button} from "@/components/ui/button"

import { useAppContext } from "@/context/AppContext";


import {
		Form,
		FormControl,
		FormDescription,
		FormField,
		FormItem,
		FormLabel,
		FormMessage,
} from "@/components/ui/form"

import {
		Select,
		SelectContent,
		SelectItem,
		SelectTrigger,
		SelectValue
} from "@/components/ui/select"
	

import samplelogs from "@/lib/sample-logs.json"

import {processAction} from "@/lib/utils"
import { errorToJSON } from "next/dist/server/render"

const formSchema = z.object({
		ddlLogDuration: z.string(),
		ddlAction: z.string()
});

export function AIInputSheet() {
	const { myAppContext, setMyAppContext } = useAppContext();  
		
	const form = useForm < z.infer < typeof formSchema >> ({
		resolver: zodResolver(formSchema)
	});
	const {formState:{errors}} = form;
	const [isSheetOpen, setIsSheetOpen] = useState(false);

	function onSubmit(values: z.infer < typeof formSchema > ) {
		try {
			const logDuration = parseInt(values.ddlLogDuration, 10);
			const action = values.ddlAction; 
			setIsSheetOpen(false);
			
			processAction(action, {duration: logDuration})
				.then((data) => {
					setMyAppContext({...myAppContext, dataTable: data});
				})
				.catch((error) => {
					console.error("Error fetching data:", error);
					toast.error("Failed to fetch data. Please try again.");
				});
			
					
			toast(
				<pre className="mt-2 w-[340px] rounded-md bg-slate-950 p-4">
					<code className="text-black">{JSON.stringify(values, null, 2)}</code>
				</pre>
			);
		} catch (error) {
			console.error("Form submission error", error);
			toast.error("Failed to submit the form. Please try again.");
		}
	}
  return (
		<Sheet
			open={isSheetOpen}
			onOpenChange={(newValue) => {
				setIsSheetOpen(newValue); // when it's closed, allow opening it
			
				// when it's opened
				// if (errors.ddlAction || errors.ddlLogDuration) setIsSheetOpen(newValue);
			
				// otherwise, don't do anything
			}}
		>
			<SheetTrigger asChild>
				<Button variant="outline">Open</Button>
			</SheetTrigger>
			
						
						
			<SheetContent>
				<SheetHeader>
					<SheetTitle>AI Log Analyser</SheetTitle>
					<SheetDescription>
							Select appropriate log duration and action to interact with AI log analyser
					</SheetDescription>
				</SheetHeader>
				<Form {...form}>
					<form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8 max-w-3xl mx-auto py-10">
						<div className="grid gap-4 py-4 px-4">
							<FormField
								control={form.control}
								name="ddlLogDuration"
								render={({ field }) => (
								<FormItem>
										<FormLabel>Log duration</FormLabel>
										<Select onValueChange={field.onChange} defaultValue={field.value}>
											<FormControl>
													<SelectTrigger>
													<SelectValue placeholder="Select log duration" />
													</SelectTrigger>
											</FormControl>
											<SelectContent>
													<SelectItem value="1">Last 1 hr</SelectItem>
													<SelectItem value="2">Last 2 hrs</SelectItem>
													<SelectItem value="6">Last 6 hrs</SelectItem>
													<SelectItem value="12">Last 12 hrs</SelectItem>
													<SelectItem value="24">Last 24 hrs</SelectItem>
													<SelectItem value="48">Last 48 hrs</SelectItem>
											</SelectContent>
										</Select>
										<FormDescription>Select the log duration (eg: Last 12hrs, Last 24hrs, Last 48hrs etc)</FormDescription>
										<FormMessage />
								</FormItem>
								)}
							/>
							
							<FormField
								control={form.control}
								name="ddlAction"
								render={({ field }) => (
									<FormItem>
										<FormLabel>Action</FormLabel>
										<Select onValueChange={field.onChange} defaultValue={field.value}>
										<FormControl>
												<SelectTrigger>
												<SelectValue placeholder="Select action" />
												</SelectTrigger>
										</FormControl>
										<SelectContent>
												<SelectItem value="rawlog">Show raw log</SelectItem>
												<SelectItem value="classifiedlog">Show AI classified log</SelectItem>
												<SelectItem value="summarylog">Show AI summarised log</SelectItem>
										</SelectContent>
										</Select>
										<FormDescription>Select which action you would like to perform</FormDescription>
										<FormMessage />
									</FormItem>
									)}
							/>
							<Button className="w-full">Send to AI</Button>
							
							
						</div>
					</form>
				</Form>
				<SheetFooter>
					&
				</SheetFooter>
			</SheetContent>
				
		</Sheet>
	)
}