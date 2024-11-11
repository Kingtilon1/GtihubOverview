'use server';

import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const body = await request.json();
    console.log('Sending request to Flask:', body);

    const response = await fetch('http://127.0.0.1:5000/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to get response from server');
    }

    const data = await response.json();

    // Format the answer to use bold formatting
    const formattedAnswer = data.answer.replace(/\*(.+?)\*/g, '**$1**');
    const formattedData = { ...data, answer: formattedAnswer };

    return NextResponse.json(formattedData);
  } catch (error) {
    console.error('Query endpoint error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}