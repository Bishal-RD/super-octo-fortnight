/**
 * API Request Middleware Module
 * 
 * This module provides middleware functionality for the Astro application to handle
 * API requests by proxying them to the backend server. It supports all HTTP methods
 * and handles errors gracefully.
 * 
 * @module middleware
 */

import type { APIContext } from 'astro';
import { defineMiddleware } from 'astro/middleware';

/**
 * The URL of the API server. Uses environment variable if set, otherwise defaults
 * to localhost for development.
 */
const API_SERVER_URL = process.env.API_SERVER_URL || 'http://localhost:5100';

/**
 * Middleware function to handle API requests by forwarding them to the backend server.
 * 
 * This middleware intercepts all requests that include '/api/' in their URL and
 * forwards them to the backend server. Other requests are passed through to regular
 * Astro handling.
 * 
 * @param {APIContext} context - The middleware context containing request information
 * @param {() => Promise<Response>} next - The next middleware function in the chain
 * @returns {Promise<Response>} The response from the API server or an error response
 * 
 * @example
 * // Example API request that will be forwarded:
 * fetch('/api/games')
 * 
 * // Example non-API request that will be handled by Astro:
 * fetch('/about')
 */
export const onRequest = defineMiddleware(async (
  context: APIContext,
  next: () => Promise<Response>
) => {
  
  // Guard clause: if not an API request, pass through to regular Astro handling
  if (!context.request.url.includes('/api/')) {
    return await next();
  }
  
  const url = new URL(context.request.url);
  const apiPath = url.pathname + url.search;
  
  // Create a new request to the backend server
  const serverRequest = new Request(`${API_SERVER_URL}${apiPath}`, {
    method: context.request.method,
    headers: context.request.headers,
    body: context.request.method !== 'GET' && context.request.method !== 'HEAD' ? 
          await context.request.clone().arrayBuffer() : undefined,
  });
  
  try {
    // Forward the request to the API server
    const response = await fetch(serverRequest);
    const data = await response.arrayBuffer();
    
    // Return the response from the API server
    return new Response(data, {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
    });
  } catch (error) {
    console.error('Error forwarding request to API:', error);
    return new Response(JSON.stringify({ error: 'Failed to reach API server' }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' }
    });
  }
});