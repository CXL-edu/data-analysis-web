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
            我们是一家创新驱动的科技公司，致力于通过技术解决方案赋能企业数字化转型。
            成立于2020年，已服务超过500家客户，覆盖金融、医疗、教育等多个领域。
          </p>
        </section>
  
        <section className="mb-16">
          <h2 className="text-2xl font-semibold mb-6">核心团队</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { name: '张三', title: 'CEO', bio: '连续创业者，10年互联网行业经验' },
              { name: '李四', title: 'CTO', bio: '前硅谷资深架构师，专注分布式系统' },
              { name: '王五', title: 'CFO', bio: '注册会计师，风险投资专家' }
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
            <p>📞 电话：+86 400-123-4567</p>
            <p>📧 邮箱：contact@company.com</p>
            <p>📍 地址：上海市浦东新区张江高科技园区</p>
          </div>
        </section>
      </div>
    );
  }