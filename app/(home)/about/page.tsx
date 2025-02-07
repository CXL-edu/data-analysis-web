export const metadata = {
    title: '关于我们',
    description: '公司简介与团队信息'
  };
  
  export default function AboutPage() {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-8 text-center">关于我们</h1>
        
        <section className="mb-16">
          <h2 className="text-2xl font-semibold mb-6">公司简介</h2>
          <p className="text-gray-600 leading-relaxed">
            我们是一家人工智能驱动的创新型科技公司，致力于通过AI技术进行数据分析，帮助用户和企业从数据驱动决策。
            成立于2025年1月，聚焦于数据分析处理、可视化、预测、故障诊断和智能决策。
          </p>
        </section>
  
        <section className="mb-16">
          <h2 className="text-2xl font-semibold mb-6">核心团队</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { name: '张三', title: 'CEO', bio: '连续创业者，5年互联网行业经验' },
              { name: '李四', title: 'CTO', bio: '资深算法工程师，专注于AI驱动的数据分析' },
              { name: '王五', title: 'CFO', bio: '风险投资专家，战略研究者' }
            ].map((member, index) => (
              <div key={index} className="p-6 bg-white rounded-lg shadow-md">
                <h3 className="text-xl font-medium mb-2">{member.name}</h3>
                <p className="text-blue-600 mb-2">{member.title}</p>
                <p className="text-gray-500">{member.bio}</p>
              </div>
            ))}
          </div>
        </section>
  
        <section>
          <h2 className="text-2xl font-semibold mb-6">联系我们</h2>
          <div className="space-y-4">
            <p>📞 电话：+86 19507416775</p>
            <p>📧 cxl_edu@foxmail.com</p>
            <p>📍 地址：深圳市福田区新一代产业园</p>
          </div>
        </section>
      </div>
    );
  }