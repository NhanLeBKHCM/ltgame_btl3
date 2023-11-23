import pygame
from support import import_csv_layout, import_cut_graphics
from settings import tile_size, screen_height
from tiles import Tile, StaticTile, Crate, AnimatedTile, Coin, Palm
from enemy import Enemy
from decoration import Sky, Water, Clouds
from player import Player
from ui import UI


class Level:
    def __init__(self, level_data, surface, change_scene):
        self.display_surface = surface
        self.world_shift = 0
        self.current_x = 0
        self.change_scene = change_scene

        # game attributes
        self.max_health = 100
        self.cur_health = 100
        self.coins = 0

        # game ui
        self.ui = UI(self.display_surface)

        # terrain setup
        terrain_layout = import_csv_layout(level_data["terrain"])
        self.terrain_sprites = self.create_tile_group(terrain_layout, "terrain")

        # grass setup
        grass_layout = import_csv_layout(level_data["grass"])
        self.grass_sprites = self.create_tile_group(grass_layout, "grass")

        # crates setup
        crate_layout = import_csv_layout(level_data["crates"])
        self.crate_sprites = self.create_tile_group(crate_layout, "crates")

        # coins setup
        coin_layout = import_csv_layout(level_data["coins"])
        self.coin_sprites = self.create_tile_group(coin_layout, "coins")

        # fg_palm setup
        fg_palm_layout = import_csv_layout(level_data["fg_palms"])
        self.fg_palm_sprites = self.create_tile_group(fg_palm_layout, "fg_palms")

        # bg_palm setup
        bg_palm_layout = import_csv_layout(level_data["bg_palms"])
        self.bg_palm_sprites = self.create_tile_group(bg_palm_layout, "bg_palms")

        # coins setup
        enemy_layout = import_csv_layout(level_data["enemies"])
        self.enemy_sprites = self.create_tile_group(enemy_layout, "enemies")

        # coins setup
        constraint_layout = import_csv_layout(level_data["constraints"])
        self.constraint_sprites = self.create_tile_group(
            constraint_layout, "constraints"
        )

        # decorations
        self.sky = Sky(7)
        level_width = len(terrain_layout[0] * tile_size)
        self.water = Water(screen_height - 20, level_width)
        self.clouds = Clouds(350, level_width, 20)

        # player
        self.player_sprite = pygame.sprite.GroupSingle()
        playerP_layout = import_csv_layout(level_data["player"])
        self.playerP_sprites = self.create_tile_group(playerP_layout, "player")
        self.player_sprite.add(
            Player(
                self.playerP_sprites.sprites()[1].rect.topleft,
                self.display_surface,
                self.change_health,
            )
        )

    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != "-1":
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == "terrain":
                        terrain_tile_list = import_cut_graphics(
                            "../graphics/terrain/terrain_tiles.png"
                        )
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == "grass":
                        grass_tile_list = import_cut_graphics(
                            "../graphics/decoration/grass/grass.png"
                        )
                        tile_surface = grass_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == "crates":
                        sprite = Crate(tile_size, x, y)

                    if type == "coins":
                        if val == "0":
                            sprite = Coin(tile_size, x, y, "../graphics/coins/gold", 3)

                        if val == "1":
                            sprite = Coin(
                                tile_size, x, y, "../graphics/coins/silver", 1
                            )

                    if type == "fg_palms":
                        if val == "1":
                            sprite = Palm(
                                tile_size, x, y, "../graphics/terrain/palm_large"
                            )
                        if val == "2":
                            sprite = Palm(
                                tile_size, x, y, "../graphics/terrain/palm_small"
                            )
                    if type == "bg_palms":
                        sprite = Palm(tile_size, x, y, "../graphics/terrain/palm_bg")

                    if type == "enemies":
                        sprite = Enemy(tile_size, x, y)

                    if type == "constraints":
                        sprite = Tile(tile_size, x, y)

                    if type == "player":
                        sprite = Tile(tile_size, x, y)

                    sprite_group.add(sprite)

        return sprite_group

    def scroll_x(self):
        player = self.player_sprite.sprite
        player_x = player.rect.center[0]
        direction_x = player.direction.x
        if player_x < 200 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > 1000 and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    def enemy_collision_reverse(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraint_sprites, False):
                enemy.reverse()

    def horizontal_movement_collision(self):
        player = self.player_sprite.sprite
        player.rect.x += player.direction.x * player.speed
        for sprite in self.terrain_sprites.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right
        if player.on_left and (
            self.current_x > player.rect.left or player.direction.x >= 0
        ):
            player.on_left = False
        if player.on_right and (
            self.current_x < player.rect.right or player.direction.x <= 0
        ):
            player.on_right = False

    def vertical_movement_collision(self):
        player = self.player_sprite.sprite
        player.apply_gravity()
        for sprite in self.terrain_sprites.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True
                elif player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0:
            player.on_ceiling = False

    def check_coin_collisions(self):
        player = self.player_sprite.sprite
        for sprite in self.coin_sprites.sprites():
            if sprite.rect.colliderect(player.rect):
                self.coins += sprite.value
                sprite.kill()

    def check_enemy_collisions(self):
        enemy_collisions = pygame.sprite.spritecollide(
            self.player_sprite.sprite, self.enemy_sprites, False
        )

        if enemy_collisions:
            for enemy in enemy_collisions:
                enemy_center = enemy.rect.centery
                enemy_top = enemy.rect.top
                player_bottom = self.player_sprite.sprite.rect.bottom
                if (
                    enemy_top < player_bottom < enemy_center
                    and self.player_sprite.sprite.direction.y >= 0
                ):
                    self.player_sprite.sprite.direction.y = -16
                    enemy.kill()
                else:
                    self.player_sprite.sprite.get_damage(25)

    def change_health(self, amount):
        self.cur_health += amount

    def check_gameover(self):
        if self.cur_health <= 0 or self.player_sprite.sprite.rect.top >= screen_height:
            self.change_scene("menu")

    def run(self):
        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface, self.world_shift)

        self.bg_palm_sprites.draw(self.display_surface)
        self.bg_palm_sprites.update(self.world_shift)

        self.terrain_sprites.draw(self.display_surface)
        self.terrain_sprites.update(self.world_shift)

        self.grass_sprites.draw(self.display_surface)
        self.grass_sprites.update(self.world_shift)

        self.crate_sprites.draw(self.display_surface)
        self.crate_sprites.update(self.world_shift)

        self.enemy_sprites.draw(self.display_surface)
        self.enemy_sprites.update(self.world_shift)
        self.constraint_sprites.update(self.world_shift)
        self.enemy_collision_reverse()

        self.player_sprite.update()
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        self.player_sprite.draw(self.display_surface)

        self.check_coin_collisions()
        self.check_enemy_collisions()

        self.coin_sprites.draw(self.display_surface)
        self.coin_sprites.update(self.world_shift)

        self.fg_palm_sprites.draw(self.display_surface)
        self.fg_palm_sprites.update(self.world_shift)

        self.water.draw(self.display_surface, self.world_shift)
        self.ui.show_health(self.cur_health, self.max_health)
        self.ui.show_coins(self.coins)
        self.check_gameover()
        self.scroll_x()
