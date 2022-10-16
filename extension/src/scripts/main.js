import { isProbablyReaderable, Readability } from '@mozilla/readability';
import * as DOMPurify from 'dompurify';

if (isProbablyReaderable(document)) {
  const documentClone = document.cloneNode(true);
  const reader = new Readability(documentClone).parse();
  const sanitized = DOMPurify.sanitize(reader.content);
  document.body.innerHTML += `<dialog>${sanitized})}<button>Close</button></dialog>`;
  const dialog = document.querySelector('dialog');
  dialog.querySelector('button').addEventListener('click', () => {
    dialog.close();
  });
  dialog.showModal();
}
