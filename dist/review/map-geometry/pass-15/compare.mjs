const versions = {
  after: ['map.webp', 'Только цвет: тёплые серо-бежевые крыши и первые жёлто-охристые оттенки в зелёной листве. Девушка, грузовики и рисунок сохранены.', 953, 830],
  before: ['../pass-14/map.png', 'Версия 14: исходные синие крыши и зелёная листва. Те же пропорции, грузовики и две фигуры девушки внутри карты.', 953, 830],
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
