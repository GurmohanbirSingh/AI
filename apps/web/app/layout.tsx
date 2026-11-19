import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "ShortsFactory AI — Local Operator",
  description: "Local-first ShortsFactory AI operator dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
