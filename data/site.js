// 网站要显示的"内容"，全都集中在这里。
// 想改标题、改文案、加作品？只动这个文件，组件代码一个字都不用碰。
// 这就是"数据与界面分离"：组件只管"怎么显示"，site.js 只管"显示什么"。
//
// 埋的那颗模块 5 的种子，现在发芽了：
// home 这份数据已经改成从后端 /api/profile 实时取（见 components/HomeView.jsx）。
// 但组件仍然保留这里的值当"打底"——静态导出时页面就是完整的，
// 后端没起来也不影响显示。所以这个文件现在有两个身份：
//   1) 构建时的默认内容（后端不可用时的兜底）
//   2) 后端 PROFILE 常量的"形状说明书"（见 backend/main.py）

export const home = {
  heroTitle: "关于我",
  heroSubtitle: "项目，创意，灵感，心得，我的作品",
  featuredWork: {
    kicker: "作品",
    title: "文字实验室",
    copy: "拼音和情绪，挖掘中文里的细节",
    linkLabel: "打开作品",
  },
  identity: {
    motto: "已识乾坤大，尤怜草木青",
    learning: "零到全栈",
  },
};

export const textLab = {
  heroTitle: "文字实验室",
  heroSubtitle: "拼音和情绪，挖掘中文里的细节",
};
