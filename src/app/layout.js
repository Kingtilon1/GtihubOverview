import "./globals.css";



export const metadata = {
  title: "GithubOvervieew",
  description: "Get info to contribute to opensource projects",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
