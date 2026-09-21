const versions = {
  after: ['map.webp', 'Версия 16: четыре разных перевозчика, лёгкий выхлоп у №1 и №4, спокойная дорожная разметка. Город и обе девушки сохранены.', 953, 830],
  before: ['../pass-15/map.png', 'Версия 15: утверждённая основа до локальной доработки грузовиков и разметки.', 953, 830],
};
for (const button of document.querySelectorAll('[data-version]')) {
  button.addEventListener('click', () => {
    const key = button.dataset.version;
    const [image, description, x, y] = versions[key];
    for (const other of document.querySelectorAll('[data-version]')) other.setAttribute('aria-pressed', String(other === button));
    document.querySelector('#art').setAttribute('href', image);
    document.querySelector('#natural').setAttribute('x', x);
    document.querySelector('#natural').setAttribute('y', y);
    document.querySelector('#description').textContent = description;
    document.querySelector('#download').href = `comparison-${key}.jpg`;
  });
}
document.querySelector('#character').addEventListener('change', event => {
  document.querySelector('#girls').style.display = event.target.checked ? '' : 'none';
});
document.querySelector('#zoom').addEventListener('change', event => {
  document.querySelector('#overview').style.width = `${Number(event.target.value) * 100}%`;
});
