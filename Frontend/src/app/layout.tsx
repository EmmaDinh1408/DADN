import type { Metadata } from "next";
import { Comfortaa, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const comfortaa = Comfortaa({
  variable: "--font-geist-sans",
  subsets: ["latin", "vietnamese"],
  weight: ["300", "400", "500", "600", "700"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin", "vietnamese"],
});

export const metadata: Metadata = {
  title: "MechDrive Studio · HCMUT",
  description: "Hệ thống thiết kế hệ dẫn động cơ khí với AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="vi"
      className={`${comfortaa.variable} ${jetbrainsMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col" style={{ fontFamily: "'Comfortaa', sans-serif" }}>{children}</body>
    </html>
  );
}

