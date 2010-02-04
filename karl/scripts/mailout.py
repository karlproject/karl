from karl.scripting import run_daemon
from repoze.sendmail.queue import ConsoleApp
from repoze.sendmail.queue import QueueProcessor

class MailOut(ConsoleApp):
    """
    While hi-jacking the repoze.sendmail console app is not strictly
    necessary, here, we gain some advantages in terms of monitoring and
    logging if we plug into karl.scripting.run_daemon as opposed to just using
    the daemonic capabilities in repoze.sendmail.queue.ConsoleApp.
    """
    def main(self):
        if self._error:
            return

        qp = QueueProcessor(self.mailer, self.queue_path)
        if self.daemon:
            run_daemon('mailout', qp.send_messages, self.interval)
        else:
            qp.send_messages()

def main():
    MailOut().main()

if __name__ == '__main__':
    main()
