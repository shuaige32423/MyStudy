/** @type {import('next').NextConfig} */
const nextConfig = {
    // 静态导出：npm run build 直接产出 out/ 目录，交给 nginx 托管。
    // 线上就不需要再跑一个 Node 进程 —— 服务器只有 1.6G 内存，能省一个是一个。
    //
    // 配套要求：构建时 NEXT_PUBLIC_API_BASE_URL 必须是【同域相对路径 /api】，
    // 由 nginx 把 /api 反代到 127.0.0.1:8000。绝对地址（http://IP:8000）会带来
    // 404 / 混合内容拦截 / 跨域三个麻烦，详见 .env.example。
    output: 'export',
};

export default nextConfig;
