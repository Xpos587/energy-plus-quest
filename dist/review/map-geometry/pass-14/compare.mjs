const versions = {
  after: ['map.jpg', 'Исходный рисунок 13 без растяжения и изгиба. Девушка — оригинал: крупно для сравнения и маленькая у бизнес-центра.', 953, 830],
  before: ['../pass-13/map.jpg', 'Отклонённая версия 13: деформация улиц и периферии. Для честного сравнения оригинальная девушка добавлена в тот же кадр.', 1020, 813],
  reference: ['../pass-12/map-a.jpg', 'Версия 12 — ориентир геометрии. Сравните прежнюю мягкую рисовку с перерисованным городом 14.', 1020, 813],
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
