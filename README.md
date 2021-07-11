# forseti
Forseti is a consensus-based cheat detection system prototype for multiplayer games.

It's not a production library by any means - it's here to demonstrate that a consensus-based cheat detection system is possible.

## When to use this method?

Consensus-based cheat detection is extremely helpful if you don't want to run your own game server architecture, but would still like some
level of protection against cheaters. Because it's based on a consensus algorithm, it's best suited for games where there are at least 4 players
against each other.

Some examples of game types where it might be good:
 - Cooperative games where cheating is not _that_ big of an issue
 - Free for all games with at least 4 players
 - Team games with at least 6 players where player parties can't exceed 2 players (think League Of Legends Duo Queue)

## What's with the name?

I was lazy and just needed to find something relevant to "fighting against crime" so I googled the "Norse god of justice". That's it really.

## Will you provide production ready libraries for X/Y technologies?

I might. I'm thinking of making at least a Unity compatible one so that anyone who uses cloud-based services like Photon or AWS Relay servers can
get away without having to set up a full fledged server based architecutre.

## How does this work?

When we think about how we play games in real life, generally speaking there are two ways games get moderated:
- There's a dedicated referee who watches everything (i.e. authoritative game server)
- Players in the game watch out for rule breakers and call them out; then they decide what the outcome should be (i.e. consensus-based cheat detection)

This repo demonstrates how one might implement the latter. It does not use actual networking but rather simulates multiple game client. This is just for the
sake of simplicity, but integrating approach into an actual multiplayer game should not be much more of a hassle.

### Cheat Detection Engine

The whole thing starts with the [Cheat Detection](https://github.com/Rockbag/forseti/blob/main/forseti/engine.py) engine. Every client needs to run this engine to be eligible to play the game. If a client fails to initialize the engine within the configured timeout period, they are automatically considered cheaters. This could happen if someone hacks the client and removes the engine from it. Now, of course, they might still just send the signal to the others saying "hey I've registered" without actually initializing the engine, but that's fine. It's just the first layer of defense.

There are many [configuration options](https://github.com/Rockbag/forseti/blob/main/forseti/engine.py#L19) for the engine, but probably the most notable one is
the `rules` parameter. This is where we define the rules of the game. We do this by mapping [Moves](https://github.com/Rockbag/forseti/blob/main/forseti/move.py) to [Rules](https://github.com/Rockbag/forseti/blob/main/forseti/rule.py).

A `Move` defines an event that is important from the game's perspective. Technically this could be anything from moving the player character, to attacking, to picking up objects, etc. Any action that's important for the game should be declared a `Move`

A `Rule` defines how a certain move should be evaluated. Typically this will resolve to a `bool` value indicating if the movement was allowed or not.

Once every client has initialised and is running its own cheat detection engine, the clients need to subscribe to other players' moves and forwrad them to the engine. Each client will then start evaluating every other clients' `Moves` against the configured `Rules`. When a client evaluates a `Move` as invalid, they will cast a vote and let the other clients know.

If enough (by default more than 50% of the) players deem an action as cheating, all clients will then unsubscribe from any other move from the cheater, essentially shadow banning them from the game. While the player might still be technically connected to the game, everyone is just going to ignore their actions from that point on.

If the game has a "leader" or "room owner" who has the ability to boot the cheater, this would be the time to do that.

An example of the engine configuration can be found in this [Virtual Client](https://github.com/Rockbag/forseti/blob/main/game/client.py).

## Where does this fail?

Typically this engine fails if there are enough clients connected to the game who are actually cheaters. It can happen that a game has multiple cheaters
running around, rendering the consensus flawed - they might not evaluate consensus or just evaluate moves incorrectly.

If that's the case, the following scenarios might happen:
 - Cheaters don't get recognised and so they stay in the game
 - Cheaters actually boot legit players (though I don't know why they would do this)

## Can I use this/rip this off

Yep! It's OS licensed, so go nuts. Just don't sue me - see the licensing info. :)
Feel free to create and sell your own lib as you wish.

## What if I need to run my own game servers after all?

If that's the case, feel free to check out my system architecture blog posts on using [AWS GameLift](https://rockbag.medium.com/building-ethoas-4702b78ec6cd) or rolling your own [On-Demand Game Server Architecture with EC2 Spot Instances](https://towardsaws.com/on-demand-game-server-architecture-on-aws-30d971261d22)
