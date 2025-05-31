'use client';

import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Card, CardContent } from "@/components/ui/card";




type SecurityEvent = {
  reasoning: string;
  event_type: string;
  requires_human_review: boolean;
  confidence_score: number;
  recommended_actions: string[];
};

type HardwareFailureEvent = SecurityEvent;

type SummaryData = {
  summary: string;
  observations: string[];
  planning: string[];
  security_events: SecurityEvent[];
  hardware_failure_events: HardwareFailureEvent[];
  requires_immediate_attention: boolean;
};

export function SummaryDisplayer({ data }: { data: SummaryData }) {
  return (
    <div className="max-w-3xl mx-auto p-4 space-y-4">
      <h1 className="text-2xl font-bold mb-4">Log Analysis Summary</h1>

      <Accordion type="multiple" defaultValue={["attention"]} className="w-full">
        
        <AccordionItem value="attention">
          <AccordionTrigger>Requires Immediate Attention</AccordionTrigger>
          <AccordionContent>
            {data.requires_immediate_attention ? (
              <p className="text-red-600 font-semibold">Yes — Immediate attention is required!</p>
            ) : (
              <p>No immediate action required.</p>
            )}
          </AccordionContent>
        </AccordionItem>
        
        <AccordionItem value="summary">
          <AccordionTrigger>Summary</AccordionTrigger>
          <AccordionContent>{data.summary}</AccordionContent>
        </AccordionItem>

        <AccordionItem value="observations">
          <AccordionTrigger>Observations</AccordionTrigger>
          <AccordionContent>
            <ul className="list-disc pl-5 space-y-1">
              {data.observations.map((obs, idx) => (
                <li key={idx}>{obs}</li>
              ))}
            </ul>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="planning">
          <AccordionTrigger>Planning</AccordionTrigger>
          <AccordionContent>
            <ul className="list-disc pl-5 space-y-1">
              {data.planning.map((plan, idx) => (
                <li key={idx}>{plan}</li>
              ))}
            </ul>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="security_events">
          <AccordionTrigger>Security Events</AccordionTrigger>
          <AccordionContent>
            {data.security_events.map((event, idx) => (
              <Card key={idx} className="mb-3">
                <CardContent className="p-4 space-y-2">
                  <p><strong>Type:</strong> {event.event_type}</p>
                  <p><strong>Reasoning:</strong> {event.reasoning}</p>
                  <p><strong>Confidence Score:</strong> {event.confidence_score}</p>
                  <p><strong>Requires Human Review:</strong> {event.requires_human_review ? 'Yes' : 'No'}</p>
                  <p><strong>Recommended Actions:</strong></p>
                  <ul className="list-disc pl-5">
                    {event.recommended_actions.map((action, i) => (
                      <li key={i}>{action}</li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="hardware_failure">
          <AccordionTrigger>Hardware Failure Events</AccordionTrigger>
          <AccordionContent>
            {data.hardware_failure_events.map((event, idx) => (
              <Card key={idx} className="mb-3">
                <CardContent className="p-4 space-y-2">
                  <p><strong>Type:</strong> {event.event_type}</p>
                  <p><strong>Reasoning:</strong> {event.reasoning}</p>
                  <p><strong>Confidence Score:</strong> {event.confidence_score}</p>
                  <p><strong>Requires Human Review:</strong> {event.requires_human_review ? 'Yes' : 'No'}</p>
                  <p><strong>Recommended Actions:</strong></p>
                  <ul className="list-disc pl-5">
                    {event.recommended_actions.map((action, i) => (
                      <li key={i}>{action}</li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </AccordionContent>
        </AccordionItem>

        
      </Accordion>
    </div>
  );
}
