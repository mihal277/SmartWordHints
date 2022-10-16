import { isProbablyReaderable, Readability } from '@mozilla/readability';

import unfluff from 'unfluff';

if (isProbablyReaderable(document)) {
  const documentClone = document.cloneNode(true);

  // const data = unfluff(document.documentElement.outerHTML);
  // console.log(data.text.replaceAll("\n\n", "<br><br>"));

  const reader = new Readability(documentClone).parse();

  // const text = data.text.replaceAll("\n\n", "<br><br>");

  document.body.innerHTML += `<dialog>This is a dialog5.<br>${reader.content})}<button>Close</button></dialog>`;
  const dialog = document.querySelector('dialog');
  dialog.querySelector('button').addEventListener('click', () => {
    dialog.close();
  });
  dialog.showModal();
}
