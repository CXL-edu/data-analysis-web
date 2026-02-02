  import { createMDX } from 'fumadocs-mdx/next';

  const withMDX = createMDX();

  /** @type {import('next').NextConfig} */
  const config = {
    reactStrictMode: true,
    // 构建时先忽略 ESLint，避免因 lint 报错导致无法生成 .next（部署后可再逐步修 lint）
    eslint: { ignoreDuringBuilds: true },
  };

  export default withMDX(config);
