import type { ReactNode } from 'react';

// 不再使用 fumadocs HomeLayout，避免搜索/主题等依赖导致客户端报错；首页导航由 Hero 自带
export default function Layout({ children }: { children: ReactNode }) {
  return <>{children}</>;
}
