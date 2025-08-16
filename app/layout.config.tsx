import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';
 

/**
 * Shared layout configurations
 *
 * you can configure layouts individually from:
 * Home Layout: app/(home)/layout.tsx
 * Docs Layout: app/docs/layout.tsx
 */
export const baseOptions: BaseLayoutProps = {
  // githubUrl: 'https://github.com/fuma-nama/fumadocs',
  nav: {
    title: <div>🌟数据分析 Agent</div>,
  },
  // nav: {
  //   // can be JSX too!
  //   title: '数据分析AI',
  // },
  links: [
    {
      text: '文档',
      url: '/docs',
      active: 'nested-url',
    },
  ],
};
