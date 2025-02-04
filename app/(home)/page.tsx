import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-fd-background">
      <main className="pt-16 flex flex-1 flex-col justify-center text-center">
        <h1 className="mb-4 text-2xl font-bold">Hello World</h1>
        <p className="text-fd-muted-foreground">
          You can open{' '}
          <Link
            href="/docs"
            className="text-fd-foreground font-semibold underline"
          >
            /docs
          </Link>{' '}
          and see the documentation.
        </p>
      </main>
    </div>
  );
}
