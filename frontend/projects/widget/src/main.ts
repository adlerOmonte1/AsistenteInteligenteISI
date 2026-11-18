import { createCustomElement } from '@angular/elements';
import { createApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { ChatWidget } from './app/chat-widget';

(async () => {
  if (customElements.get('udh-chat')) return;
  const app = await createApplication(appConfig);
  const elemento = createCustomElement(ChatWidget, { injector: app.injector });
  customElements.define('udh-chat', elemento);
})().catch((error) => console.error('No se pudo iniciar <udh-chat>', error));
