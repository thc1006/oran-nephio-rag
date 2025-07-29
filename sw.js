// Service Worker for O-RAN × Nephio RAG Website
// Version 1.0.0

const CACHE_NAME = 'oran-nephio-rag-v1.0.0';
const urlsToCache = [
    '/oran-nephio-rag/',
    '/oran-nephio-rag/docs/',
    '/oran-nephio-rag/assets/styles/main.css',
    '/oran-nephio-rag/assets/scripts/main.js',
    '/oran-nephio-rag/assets/images/og-image.png',
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap'
];

// Install event - cache resources
self.addEventListener('install', function(event) {
    console.log('Service Worker: Installing...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('Service Worker: Caching files');
                return cache.addAll(urlsToCache);
            })
            .then(function() {
                console.log('Service Worker: Installed');
                return self.skipWaiting();
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', function(event) {
    console.log('Service Worker: Activating...');
    
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Service Worker: Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(function() {
            console.log('Service Worker: Activated');
            return self.clients.claim();
        })
    );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', function(event) {
    // Skip cross-origin requests
    if (!event.request.url.startsWith(self.location.origin)) {
        return;
    }
    
    // Skip non-GET requests
    if (event.request.method !== 'GET') {
        return;
    }
    
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // Return cached version or fetch from network
                if (response) {
                    console.log('Service Worker: Serving from cache:', event.request.url);
                    return response;
                }
                
                console.log('Service Worker: Fetching from network:', event.request.url);
                return fetch(event.request).then(function(response) {
                    // Don't cache if not a valid response
                    if (!response || response.status !== 200 || response.type !== 'basic') {
                        return response;
                    }
                    
                    // Clone the response
                    const responseToCache = response.clone();
                    
                    // Add to cache
                    caches.open(CACHE_NAME)
                        .then(function(cache) {
                            cache.put(event.request, responseToCache);
                        });
                    
                    return response;
                }).catch(function(error) {
                    console.log('Service Worker: Fetch failed:', error);
                    
                    // Return offline page for navigation requests
                    if (event.request.destination === 'document') {
                        return caches.match('/oran-nephio-rag/offline.html');
                    }
                });
            })
    );
});

// Background sync for form submissions
self.addEventListener('sync', function(event) {
    if (event.tag === 'demo-query-sync') {
        event.waitUntil(syncDemoQueries());
    }
});

async function syncDemoQueries() {
    // Handle offline demo queries when back online
    try {
        const queries = await getStoredQueries();
        for (const query of queries) {
            // Process stored queries
            console.log('Processing stored query:', query);
        }
        await clearStoredQueries();
    } catch (error) {
        console.error('Sync failed:', error);
    }
}

async function getStoredQueries() {
    // Implementation would depend on IndexedDB storage
    return [];
}

async function clearStoredQueries() {
    // Clear processed queries from storage
    return true;
}

// Push notification handling
self.addEventListener('push', function(event) {
    console.log('Service Worker: Push received');
    
    const options = {
        body: event.data ? event.data.text() : 'New update available!',
        icon: '/oran-nephio-rag/assets/images/icon-192x192.png',
        badge: '/oran-nephio-rag/assets/images/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: '查看更新',
                icon: '/oran-nephio-rag/assets/images/checkmark.png'
            },
            {
                action: 'close',
                title: '關閉',
                icon: '/oran-nephio-rag/assets/images/xmark.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('O-RAN × Nephio RAG', options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', function(event) {
    console.log('Service Worker: Notification click received');
    
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/oran-nephio-rag/')
        );
    } else if (event.action === 'close') {
        // Just close the notification
        return;
    } else {
        // Default action - open the main page
        event.waitUntil(
            clients.openWindow('/oran-nephio-rag/')
        );
    }
});

// Message handling from main thread
self.addEventListener('message', function(event) {
    console.log('Service Worker: Message received:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'GET_VERSION') {
        event.ports[0].postMessage({
            version: CACHE_NAME
        });
    }
});

// Error handling
self.addEventListener('error', function(event) {
    console.error('Service Worker: Error occurred:', event.error);
});

self.addEventListener('unhandledrejection', function(event) {
    console.error('Service Worker: Unhandled promise rejection:', event.reason);
});

// Periodic background sync (if supported)
self.addEventListener('periodicsync', function(event) {
    if (event.tag === 'update-check') {
        event.waitUntil(checkForUpdates());
    }
});

async function checkForUpdates() {
    try {
        // Check for application updates
        const response = await fetch('/oran-nephio-rag/api/version');
        const data = await response.json();
        
        if (data.version !== CACHE_NAME) {
            // New version available
            self.registration.showNotification('更新可用', {
                body: '有新版本的 O-RAN × Nephio RAG 可用',
                icon: '/oran-nephio-rag/assets/images/icon-192x192.png',
                tag: 'update-available'
            });
        }
    } catch (error) {
        console.error('Update check failed:', error);
    }
}

console.log('Service Worker: Script loaded');