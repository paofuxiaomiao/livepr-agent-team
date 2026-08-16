const progressBar = document.querySelector('.reading-progress span');
const menuButton = document.querySelector('.menu-button');
const mobileMenu = document.querySelector('.mobile-menu');
const mobileLinks = [...document.querySelectorAll('.mobile-menu a')];
const indexLinks = [...document.querySelectorAll('.section-index a[data-target]')];
const sections = [...document.querySelectorAll('[data-section]')];
const revealItems = [...document.querySelectorAll('.reveal')];

const updateProgress = () => {
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const progress = scrollable > 0 ? window.scrollY / scrollable : 0;
  progressBar.style.transform = `scaleX(${Math.min(Math.max(progress, 0), 1)})`;
};

const setActiveSection = (sectionId) => {
  indexLinks.forEach((link) => {
    const active = link.dataset.target === sectionId;
    link.classList.toggle('active', active);
    if (active) link.setAttribute('aria-current', 'true');
    else link.removeAttribute('aria-current');
  });
};

const closeMenu = () => {
  menuButton?.setAttribute('aria-expanded', 'false');
  menuButton?.setAttribute('aria-label', '打开章节目录');
  mobileMenu?.setAttribute('aria-hidden', 'true');
  mobileMenu?.classList.remove('open');
  document.body.classList.remove('menu-open');
};

const openMenu = () => {
  menuButton?.setAttribute('aria-expanded', 'true');
  menuButton?.setAttribute('aria-label', '关闭章节目录');
  mobileMenu?.setAttribute('aria-hidden', 'false');
  mobileMenu?.classList.add('open');
  document.body.classList.add('menu-open');
};

menuButton?.addEventListener('click', () => {
  if (mobileMenu?.classList.contains('open')) closeMenu();
  else openMenu();
});

mobileLinks.forEach((link) => link.addEventListener('click', closeMenu));

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') closeMenu();
});

window.addEventListener('resize', () => {
  if (window.innerWidth > 820) closeMenu();
});

if ('IntersectionObserver' in window) {
  const revealObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      });
    },
    { rootMargin: '0px 0px -10% 0px', threshold: 0.08 },
  );

  revealItems.forEach((item) => revealObserver.observe(item));

  const sectionObserver = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (visible) setActiveSection(visible.target.dataset.section);
    },
    { rootMargin: '-20% 0px -58% 0px', threshold: [0.05, 0.2, 0.5] },
  );

  sections.forEach((section) => sectionObserver.observe(section));
} else {
  revealItems.forEach((item) => item.classList.add('visible'));
}

window.addEventListener('scroll', updateProgress, { passive: true });
updateProgress();
