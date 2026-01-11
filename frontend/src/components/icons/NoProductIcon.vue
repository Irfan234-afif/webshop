<template>
    <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <!-- Background -->
        <rect width="200" height="200" fill="#f3f4f6" />

        <!-- Image icon centered -->
        <g transform="translate(60, 55)">
            <!-- Frame -->
            <rect x="0" y="0" width="80" height="60" rx="4" fill="none" stroke="#9ca3af" stroke-width="3" />

            <!-- Mountain/landscape -->
            <path d="M 10 45 L 25 28 L 40 40 L 55 25 L 70 40 L 70 50 L 10 50 Z" fill="#d1d5db" />

            <!-- Sun/circle -->
            <circle cx="60" cy="18" r="7" fill="#e5e7eb" />
        </g>

        <!-- Text centered -->
        <text x="100" y="140" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#6b7280">
            No Image
        </text>
    </svg>
</template>