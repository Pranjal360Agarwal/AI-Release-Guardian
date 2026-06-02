import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Release Guardian",
  description: "AI-native release risk analysis for GitHub pull requests",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
