import { NextResponse } from 'next/server';

const TODOIST_API_KEY = process.env.TODOIST_API_KEY;

export async function GET() {
  if (!TODOIST_API_KEY) {
    return NextResponse.json(
      { error: 'TODOIST_API_KEY not configured' },
      { status: 500 }
    );
  }

  try {
    const response = await fetch('https://api.todoist.com/rest/v2/tasks', {
      headers: {
        Authorization: `Bearer ${TODOIST_API_KEY}`,
      },
      next: { revalidate: 60 }, // Cache for 60 seconds
    });

    if (!response.ok) {
      throw new Error(`Todoist API error: ${response.status}`);
    }

    const tasks = await response.json();
    return NextResponse.json(tasks);
  } catch (error) {
    console.error('Failed to fetch Todoist tasks:', error);
    return NextResponse.json(
      { error: 'Failed to fetch tasks' },
      { status: 500 }
    );
  }
}
