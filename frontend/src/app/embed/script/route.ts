export async function GET() {
  const js = `
    (function () {
      const containers = document.querySelectorAll('[data-ttl-profile]');
      
      containers.forEach(el => {
        const id = el.getAttribute('data-ttl-profile');
        
        const iframe = document.createElement('iframe');
        iframe.src = "https://trading-truth-layer.vercel.app/embed/profile/" + id;
        iframe.width = "100%";
        iframe.height = "400";
        iframe.style.border = "none";
        
        el.appendChild(iframe);
      });
    })();
  `;

  return new Response(js, {
    headers: {
      "Content-Type": "application/javascript",
    },
  });
}