import asyncio

from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import defer_call, info as session_info, run_async

MAX_MESSAGES_CNT = 10 ** 4

chat_msgs = []  # The chat message history. The item is (name, message content)
online_users = set()


def t(eng, chinese):
    """return English or Chinese text according to the user's browser language"""
    return chinese if 'zh' in session_info.user_language else eng


async def refresh_msg(my_name):
    """send new message to current session"""
    global chat_msgs
    last_idx = len(chat_msgs)
    while True:
        await asyncio.sleep(0.5)
        for m in chat_msgs[last_idx:]:
            if m[0] != my_name:  # only refresh message that not sent by current user
                put_markdown('`%s`: %s' % m, sanitize=True, scope='msg-box')

        # remove expired message
        if len(chat_msgs) > MAX_MESSAGES_CNT:
            chat_msgs = chat_msgs[len(chat_msgs) // 2:]

        last_idx = len(chat_msgs)


async def main():
    """PyWebIO chat room

    You can chat with everyone currently online.
    """
    global chat_msgs

    put_markdown(t("## Чат комната SKN KAN\n)

    put_scrollable(put_scope('msg-box'), height=300, keep_bottom=True)
    nickname = await input(t("Ваше имя", "请输入你的昵称"), required=True, validate=lambda n: t('Извините,имя уже используется')

    online_users.add(nickname)
    chat_msgs.append(('📢', '`%s` Вошел  %s Онлайн' % (nickname, len(online_users))))
    put_markdown('`📢`: `%s` Вошел %s Онлайн' % (nickname, len(online_users)), sanitize=True, scope='msg-box')

    @defer_call
    def on_close():
        online_users.remove(nickname)
        chat_msgs.append(('📢', '`%s` Вышел %s Теперь онлайн' % (nickname, len(online_users))))

    refresh_task = run_async(refresh_msg(nickname))

    while True:
        data = await input_group(t('Отправить', '发送消息'), [
            input(name='msg', help_text=t('Просим быть дружелюбными', '消息内容支持行内Markdown语法')),
            actions(name='cmd', buttons=[t('Send', '发送'), t('Multiline Input', '多行输入'), {'label': t('Exit', '退出'), 'type': 'cancel'}])
        ], validate=lambda d: ('msg', 'Напишите пожалуйста сообщение') if d['cmd'] == t('Send', '发送') and not d['msg'] else None)
        if data is None:
            break
        if data['cmd'] == t('Больше  ', '多行输入'):
            data['msg'] = '\n' + await textarea('Напишите сообщениеt=t('Просим быть дружелюбными', '消息内容支持Markdown语法'))
        put_markdown('`%s`: %s' % (nickname, data['msg']), sanitize=True, scope='msg-box')
        chat_msgs.append((nickname, data['msg']))

    refresh_task.close()
    toast("Вы вышли")


if __name__ == '__main__':
    start_server(main, debug=True, port=8080)