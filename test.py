import asyncio


async def test():
    print(1)
    await asyncio.sleep(0)
    
    print(2)
    await asyncio.sleep(0)
    
    print(3)


def main():
    x = test()
    x.send(None)
    x.send(None)


if __name__ == '__main__':
    main()
