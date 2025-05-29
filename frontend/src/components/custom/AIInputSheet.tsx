import {
  Sheet,
//   SheetClose,
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
import { RotateCcw } from "lucide-react";

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
	
import { Input } from "@/components/ui/input"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
// import samplelogs from "@/lib/sample-logs.json"

import {processAction} from "@/lib/utils"
// import { errorToJSON } from "next/dist/server/render"

import jsondata from "@/lib/summarize.json" assert { type: "json" };


const formSchema = z.object({
		ddlLogDuration: z.string(),
		ddlAction: z.string(),
		filepath: z.string().nullable().optional(),
});

const formFreeHandSchema = z.object({
	filepath: z.string(),
	totalrows: z.string(),
	skiprows: z.string().nullable().optional(),
});

export function AIInputSheet() {
	const { myAppContext, setMyAppContext } = useAppContext();  
		
	const form = useForm < z.infer < typeof formSchema >> ({
		resolver: zodResolver(formSchema)
	});


	const formFreeHand = useForm < z.infer < typeof formFreeHandSchema >> ({
		resolver: zodResolver(formFreeHandSchema)
	});

	const {formState:{errors}} = form;
	// const {formFreeHandState:{errors}} = formFreeHand;
	const [isSheetOpen, setIsSheetOpen] = useState(false);

	function onSubmit(values: z.infer < typeof formSchema > ) {
		try {
			const logDuration = parseInt(values.ddlLogDuration, 10);
			const action = values.ddlAction; 
			const filepath = values.filepath; 
			setIsSheetOpen(false);
			
			processAction(myAppContext.ENVVARS.AIBACKEND_SERVER, action, {duration: logDuration, filepath: filepath})
				.then((data) => {
					if(typeof data === "object" && data !== null) {
						if ("action" in data) {
							if(data.action === "summarize") {
								console.log("HERE");
								// setMyAppContext({...myAppContext, summarydata: data});
								if ('message' in data) {
									// sendMessage(data.message as string, "assistant");
									console.log(data)
								} else {
									console.error("Property 'message' does not exist on the data object:", data);
									toast.error("Failed to process the response. Missing 'message' property.");
								}
							} else if(data.action === "jsonsummary") {
								setMyAppContext({...myAppContext, summarydata: data});
							} else {
								setMyAppContext({...myAppContext, dataTable: data});
							}
						  
						} else {
						  throw new Error(JSON.stringify(data));
						}
					  } else {
						throw new Error("fetched data from AI machine is null or undefined. ERROR: "+data);
					  }
				})
				.catch((error) => {
					console.error("Error fetching data:", error);
					toast.error("Failed to fetch data. Please try again.");
				});
			
					
			toast(
				<pre className="mt-2 w-[340px] max-h-[200px] rounded-md p-4 overflow-y-auto whitespace-pre-wrap break-words">
					<code className="text-black">{JSON.stringify(values, null, 2)}</code>
				</pre>
			);
		} catch (error) {
			console.error("Form submission error", error);
			toast.error("Failed to submit the form. Please try again.");
		}
	}


	function onSubmitFreeHand(values: z.infer < typeof formFreeHandSchema > ) {
		try {
			const filepath = values.filepath;
			const totalrows = values.totalrows;
			const skiprows = values.skiprows;
			setIsSheetOpen(false);
			
			processAction(myAppContext.ENVVARS.AIBACKEND_SERVER, "truncatecsv", {filepath: filepath, totalrows: totalrows, skiprows: skiprows})
				.then((data) => {
					setMyAppContext({...myAppContext, dataTable: data});
				})
				.catch((error) => {
					console.error("Error fetching data:", error);
					toast.error("Failed to fetch data. Please try again.");
				});
			
					
			toast(
				<pre className="mt-2 w-[340px] max-h-[200px] rounded-md p-4 overflow-y-auto whitespace-pre-wrap break-words">
					<code>{JSON.stringify(values, null, 2)}</code>
				</pre>
			);
		} catch (error) {
			console.error("Form submission error", error);
			toast.error("Failed to submit the form. Please try again.");
		}
	}

	function listFiles () {
		processAction(myAppContext.ENVVARS.AIBACKEND_SERVER, "listfiles", {})
		.then((data) => {
			setMyAppContext({...myAppContext, fileslist: data});
		})
		.catch((error) => {
			console.error("Error fetching data:", error);
			toast.error("Failed to fetch file list in /tmp/logs/ dir. Please try again.");
		});
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

				<Accordion type="multiple" className="px-5">
					<AccordionItem value="sendtoai">
						<AccordionTrigger>Send to AI</AccordionTrigger>
						<AccordionContent>
							<Form {...form}>
								<form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8 max-w-3xl mx-auto">
									<div className="grid gap-4 px-4">
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
											name="filepath"
											render={({ field }) => (
											<FormItem>
												<FormLabel>File path</FormLabel>
												<Input type="text" placeholder="Enter file path" {...field} value={field.value ?? ""} />
												
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
															<SelectItem value="summarizelogs">summarised log</SelectItem>
															<SelectItem value="jsonsummary">Load JSON Summary</SelectItem>
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

						</AccordionContent>
					</AccordionItem>

					<AccordionItem value="truncate">
						<AccordionTrigger>Truncate CSV</AccordionTrigger>
						<AccordionContent>
							<Form {...formFreeHand}>
								<form onSubmit={formFreeHand.handleSubmit(onSubmitFreeHand)} className="space-y-8 max-w-3xl mx-auto py-1">
									<div className="grid gap-4 py-4 px-4">
										<FormField
											control={formFreeHand.control}
											name="filepath"
											render={({ field }) => (
											<FormItem>
													<FormLabel>File Path</FormLabel>
													<Input type="text" placeholder="Enter file path" {...field} />
													
													<FormMessage />
											</FormItem>
											)}
										/>
										
										<FormField
											control={formFreeHand.control}
											name="totalrows"
											render={({ field }) => (
												<FormItem>
													<FormLabel>Total Rows</FormLabel>
													<Input type="text" placeholder="Enter total rows (useful for trucating from bottom)" {...field} />
													
													<FormMessage />
												</FormItem>
												)}
										/>

										<FormField
											control={formFreeHand.control}
											name="skiprows"
											render={({ field }) => (
											<FormItem>
												<FormLabel>Skip rows</FormLabel>
												<Input type="text" placeholder="Enter row to skip (useful for trucating from top)" {...field} value={field.value ?? ""} />
												
												<FormMessage />
											</FormItem>
											)}
										/>
										
										<Button className="w-full">Truncate</Button>
										
										
									</div>
								</form>
							</Form>

						</AccordionContent>
					</AccordionItem>
				</Accordion>

				
				
				<div className="border rounded p-4 bg-white dark:bg-gray-800 shadow-md">
					<h2 className="text-lg font-semibold mb-2">Files List</h2>
					<Button variant="outline" size="icon" onClick={listFiles}>
						<RotateCcw className="h-4 w-4" />
						<span className="sr-only">Refresh</span>
					</Button>
					{myAppContext.fileslist && myAppContext.fileslist.length > 0 && (
						<ul className="list-disc list-inside space-y-1">
						{myAppContext.fileslist.map((filePath: string, index: number) => (
							<li key={index} className="break-all text-sm text-gray-800 dark:text-gray-200">
							{filePath}
							</li>
						))}
						</ul>
					)}
				</div>
				<SheetFooter>
					<Button className="w-20" onClick={() => setMyAppContext({...myAppContext, summarydata: jsondata})}>sample</Button>
				</SheetFooter>
			</SheetContent>
				
		</Sheet>
	)
}