// Sidebar按钮样式配置
export const buttonStyles = {
  // 主要操作按钮（强调色）
  primary: {
    base: 'bg-blue-600 hover:bg-blue-700 text-white',
    collapsed: 'p-3',
    expanded: 'px-4 py-3'
  },
  // 次要操作按钮（中性色）
  secondary: {
    base: 'bg-gray-100 hover:bg-gray-200 text-gray-700',
    collapsed: 'p-3',
    expanded: 'px-4 py-3'
  },
  // 共同样式
  common: 'w-full rounded-lg font-medium transition-colors'
} as const;

// 获取按钮完整样式的工具函数
export const getButtonClassName = (
  type: 'primary' | 'secondary',
  isCollapsed: boolean,
  additionalClasses?: string
): string => {
  const style = buttonStyles[type];
  const sizeClass = isCollapsed ? style.collapsed : style.expanded;
  return `${buttonStyles.common} ${style.base} ${sizeClass}${additionalClasses ? ` ${additionalClasses}` : ''}`;
};
