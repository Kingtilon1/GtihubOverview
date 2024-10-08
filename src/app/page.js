'use client'
import { useState, useEffect } from 'react';

export default function Home() {
  const [message, setMessage] = useState('')

  useEffect(() =>{
    async function fetchHelloWorld(){
      try{
        const response = await fetch('http://127.0.0.1:5000/')
        const result = await response.json();
        setMessage(result.message)
      }catch(error){
        console.error('Error fetching data:',error)
      }
    }
    fetchHelloWorld();
  }, [])

  return (
   <div>Hello {message}</div>
  );
}
