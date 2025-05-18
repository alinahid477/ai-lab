import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    WSSERVER: process.env.WSSERVER ?? null,
    AIBACKEND_SERVER: process.env.AIBACKEND_SERVER ?? null,
  });
}