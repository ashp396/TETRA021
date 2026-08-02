import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Finvestor",
  description: "Fundraising readiness, checked before your investor does.",
};
 
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
