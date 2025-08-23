import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';


/**
 * Shared layout configurations
 *
 * you can configure layouts individually from:
 * Home Layout: app/(home)/layout.tsx
 * Docs Layout: app/docs/layout.tsx
 */
export const baseOptions: BaseLayoutProps = {
  nav: {
    // 加上自己的icon '/favicon1.svg'
    title: (
      <>
        <img
          src="/favicon1.svg"
          alt="Logo"
          width={24}
          height={24}
          className="inline-block"
        />
        数源智能
      </>
    ),
  },
  // githubUrl: 'https://github.com/fuma-nama/fumadocs',
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
